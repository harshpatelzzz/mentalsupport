from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4
import json

from app.db.session import get_db
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatHistoryRequest
from app.models.chat import SenderType
from app.models.visitor import Visitor
from app.services.chat_service import chat_service
from app.websocket.connection_manager import manager
from app.core.logging import logger

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/session/create")
def create_chat_session(
    visitor_name: str = None,
    db: Session = Depends(get_db)
):
    """
    Create a new chat session with optional visitor name.
    Returns session_id and visitor_id for tracking.
    """
    # Create visitor
    visitor = Visitor(name=visitor_name)
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    
    # Generate session ID
    session_id = uuid4()
    
    logger.info(f"Created chat session {session_id} for visitor {visitor.id}")
    
    return {
        "session_id": str(session_id),
        "visitor_id": str(visitor.id),
        "visitor_name": visitor_name
    }


@router.post("/messages", response_model=ChatMessageResponse)
def create_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new chat message.
    Used for HTTP-based message creation (fallback for WebSocket).
    """
    try:
        chat_message = chat_service.create_message(db, message)
        return chat_message
    except Exception as e:
        logger.error(f"Error creating message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/messages/{session_id}", response_model=List[ChatMessageResponse])
def get_chat_history(
    session_id: UUID,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve chat history for a session.
    """
    messages = chat_service.get_chat_history(db, session_id, limit)
    return messages


@router.get("/session/{session_id}/stats")
def get_session_stats(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a chat session.
    """
    stats = chat_service.get_session_stats(db, session_id)
    return stats


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat.
    Handles message exchange, emotion analysis, and AI responses.
    """
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "typing":
                # Broadcast typing indicator
                await manager.send_typing_indicator(
                    session_id,
                    message_data.get("sender_type", "visitor"),
                    message_data.get("is_typing", False)
                )
                continue
            
            # Create message in database
            message_create = ChatMessageCreate(
                session_id=UUID(session_id),
                sender_type=SenderType(message_data.get("sender_type", "visitor")),
                content=message_data.get("content", ""),
                visitor_id=UUID(message_data["visitor_id"]) if message_data.get("visitor_id") else None
            )
            
            # Save message
            chat_message = chat_service.create_message(db, message_create)
            
            # Broadcast message to all session participants
            message_response = {
                "type": "message",
                "id": str(chat_message.id),
                "session_id": str(chat_message.session_id),
                "sender_type": chat_message.sender_type.value,
                "content": chat_message.content,
                "emotion": chat_message.emotion,
                "confidence": chat_message.confidence,
                "created_at": chat_message.created_at.isoformat()
            }
            
            await manager.broadcast_to_session(message_response, session_id)
            
            # Generate AI response if message is from visitor
            if message_create.sender_type == SenderType.VISITOR:
                # Send typing indicator
                await manager.send_typing_indicator(session_id, "ai", True)
                
                # Generate AI response
                ai_response_content = chat_service.get_ai_response(message_create.content)
                
                # Stop typing indicator
                await manager.send_typing_indicator(session_id, "ai", False)
                
                # Create AI message
                ai_message_create = ChatMessageCreate(
                    session_id=UUID(session_id),
                    sender_type=SenderType.AI,
                    content=ai_response_content,
                    visitor_id=None
                )
                
                ai_message = chat_service.create_message(db, ai_message_create)
                
                # Broadcast AI response
                ai_message_response = {
                    "type": "message",
                    "id": str(ai_message.id),
                    "session_id": str(ai_message.session_id),
                    "sender_type": ai_message.sender_type.value,
                    "content": ai_message.content,
                    "emotion": ai_message.emotion,
                    "confidence": ai_message.confidence,
                    "created_at": ai_message.created_at.isoformat()
                }
                
                await manager.broadcast_to_session(ai_message_response, session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info(f"Client disconnected from session {session_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error in session {session_id}: {e}")
        manager.disconnect(websocket, session_id)
