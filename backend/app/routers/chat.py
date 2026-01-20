from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
import json
import re

from app.db.session import get_db
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatHistoryRequest
from app.models.chat import SenderType
from app.models.visitor import Visitor
from app.models.chat_escalation import ChatEscalation
from app.models.appointment import Appointment, ChatMode
from app.services.chat_service import chat_service
from app.services.chat_health_service import chat_health_service
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


@router.post("/therapist/join/{appointment_id}")
async def therapist_join_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Therapist joins an appointment chat.
    Sets chat_mode to THERAPIST_JOINED and notifies the user.
    """
    logger.info(f"🧑‍⚕️ Therapist joining appointment {appointment_id}")
    
    # Get appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update chat mode to THERAPIST_JOINED
    appointment.chat_mode = ChatMode.THERAPIST_JOINED
    db.commit()
    
    logger.info(f"✅ Appointment {appointment_id} chat_mode changed to THERAPIST_JOINED")
    
    # Send system message to notify user
    system_message = {
        "type": "message",  # Changed from "system" to "message" so frontend displays it
        "sender": "system",
        "content": "🧑‍⚕️ Therapist has joined. You can talk directly now.",
        "session_id": str(appointment.session_id),
        "timestamp": datetime.utcnow().isoformat(),
        "emotion": None,
        "confidence": None
    }
    
    await manager.broadcast_to_session(system_message, str(appointment.session_id))
    logger.warning(f"📢 Sent therapist join notification to session {appointment.session_id}")
    
    return {
        "status": "ok",
        "appointment_id": str(appointment_id),
        "session_id": str(appointment.session_id),
        "chat_mode": appointment.chat_mode.value
    }


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
            
            # Handle typing indicators
            if message_data.get("type") == "typing":
                await manager.send_typing_indicator(
                    session_id,
                    message_data.get("sender", "user"),
                    message_data.get("is_typing", False)
                )
                continue
            
            # Extract sender and content
            sender = message_data.get("sender", "user")  # "user" | "therapist" | "ai"
            content = message_data.get("content", "")
            
            if not content.strip():
                continue
            
            logger.info(f"📨 Received message from '{sender}' in session {session_id}")
            
            # Map sender to SenderType enum
            sender_type_map = {
                "user": SenderType.VISITOR,
                "therapist": SenderType.THERAPIST,
                "ai": SenderType.AI
            }
            sender_type = sender_type_map.get(sender, SenderType.VISITOR)
            
            # Save message to database
            message_create = ChatMessageCreate(
                session_id=UUID(session_id),
                sender_type=sender_type,
                content=content,
                visitor_id=UUID(message_data["visitor_id"]) if message_data.get("visitor_id") else None
            )
            chat_message = chat_service.create_message(db, message_create)
            
            # Broadcast message to all participants
            message_response = {
                "type": "message",
                "id": str(chat_message.id),
                "session_id": str(chat_message.session_id),
                "sender": sender,  # Use "sender" not "sender_type"
                "content": chat_message.content,
                "emotion": chat_message.emotion,
                "confidence": chat_message.confidence,
                "created_at": chat_message.created_at.isoformat()
            }
            await manager.broadcast_to_session(message_response, session_id)
            logger.info(f"✅ Broadcasted message from '{sender}'")
            
            # 🚨 CRITICAL: Check appointment mode BEFORE any AI logic
            # Fetch appointment from DB (always get latest state)
            appointment = db.query(Appointment)\
                .filter(Appointment.session_id == UUID(session_id))\
                .first()
            
            # DEBUG: Log current chat mode
            if appointment:
                logger.warning(f"📊 DEBUG - Session {session_id} | CHAT_MODE: {appointment.chat_mode.value}")
            else:
                logger.warning(f"⚠️ DEBUG - Session {session_id} | No appointment found (chat_mode will default to BOT_ONLY)")
            
            # If therapist has joined, ONLY broadcast (no bot replies)
            if appointment and appointment.chat_mode == ChatMode.THERAPIST_JOINED:
                logger.warning(f"🧑‍⚕️ THERAPIST_JOINED mode - Bot will NOT respond")
                continue  # Skip all AI logic
            
            # Only generate AI response if sender is "user" AND mode is BOT_ONLY
            if sender == "user":
                logger.info(f"🤖 BOT_ONLY mode - Generating AI response")
                
                # ============================================
                # STEP 1: Check if ANY escalation exists for this session
                # ============================================
                any_existing_escalation = db.query(ChatEscalation)\
                    .filter(ChatEscalation.session_id == UUID(session_id))\
                    .first()
                
                # ============================================
                # STEP 2: If escalation exists and pending, check for user response
                # ============================================
                if any_existing_escalation and any_existing_escalation.user_accepted == "pending":
                    user_content_lower = message_create.content.lower().strip()
                    
                    # Check for acceptance
                    if any(word in user_content_lower for word in ["yes", "okay", "ok", "sure", "book", "please", "confirm"]):
                        logger.info(f"✅ User ACCEPTED escalation for session {session_id}")
                        any_existing_escalation.user_accepted = "accepted"
                        any_existing_escalation.resolved_at = datetime.utcnow()
                        db.commit()
                        
                        # Send acceptance confirmation
                        confirmation_message = {
                            "type": "ESCALATION_ACCEPTED",
                            "session_id": session_id,
                            "message": "Perfect! Let me book an appointment for you right away..."
                        }
                        await manager.broadcast_to_session(confirmation_message, session_id)
                        continue  # Don't generate AI response
                    
                    # Check for decline
                    elif any(word in user_content_lower for word in ["no", "not now", "later", "maybe later", "decline", "nope"]):
                        logger.info(f"❌ User DECLINED escalation for session {session_id}")
                        any_existing_escalation.user_accepted = "declined"
                        any_existing_escalation.resolved_at = datetime.utcnow()
                        db.commit()
                        # Continue to AI response below
                
                # ============================================
                # STEP 3: IMMEDIATE INTENT CHECK (if no escalation exists yet)
                # ============================================
                if not any_existing_escalation:
                    logger.warning(f"=" * 80)
                    logger.warning(f"🔍 CHECKING FOR ESCALATION INTENT")
                    logger.warning(f"Session: {session_id}")
                    logger.warning(f"Message: '{message_create.content}'")
                    logger.warning(f"=" * 80)
                    
                    # 🚨 CRITICAL: Check for direct escalation intent FIRST
                    intent_detected = chat_health_service.has_direct_escalation_intent(message_create.content)
                    
                    if intent_detected:
                        logger.warning(f"🚨" * 30)
                        logger.warning(f"🚨 ESCALATION INTENT DETECTED - STOPPING AI RESPONSE 🚨")
                        logger.warning(f"🚨 Session: {session_id}")
                        logger.warning(f"🚨 Message: '{message_create.content}'")
                        logger.warning(f"🚨" * 30)
                        
                        # Create escalation record
                        new_escalation = ChatEscalation(
                            session_id=UUID(session_id),
                            reason="user_request",
                            user_accepted="pending"
                        )
                        db.add(new_escalation)
                        db.commit()
                        db.refresh(new_escalation)
                        logger.warning(f"✅ Escalation record created: ID={new_escalation.id}")
                        
                        # Send SYSTEM_SUGGESTION immediately
                        system_message = {
                            "type": "SYSTEM_SUGGESTION",
                            "session_id": session_id,
                            "message": "I understand you'd like to speak with a therapist. Would you like me to book an appointment for you right away?",
                            "reason": "user_request"
                        }
                        logger.warning(f"📤 Broadcasting SYSTEM_SUGGESTION to all connections in session {session_id}")
                        await manager.broadcast_to_session(system_message, session_id)
                        logger.warning(f"✅ SYSTEM_SUGGESTION broadcast complete")
                        
                        # 🛑 CRITICAL: STOP EXECUTION - Do NOT continue to AI response
                        logger.warning(f"🛑 RETURNING NOW - NO AI RESPONSE WILL BE GENERATED 🛑")
                        logger.warning(f"=" * 80)
                        continue  # THIS SKIPS THE AI RESPONSE GENERATION BELOW
                    
                    logger.info(f"✅ No direct intent detected, checking chat health...")
                    
                    # Check for chat health issues (AI looping, emotions, etc.)
                    logger.info(f"No direct intent detected, checking chat health...")
                    recent_messages = chat_service.get_chat_history(db, UUID(session_id), limit=10)
                    
                    if chat_health_service.should_trigger_escalation(recent_messages, False):
                        health_result = chat_health_service.evaluate_chat_health(recent_messages)
                        logger.warning(f"Chat health issue detected: {health_result['reason']}")
                        
                        # Create escalation record
                        new_escalation = ChatEscalation(
                            session_id=UUID(session_id),
                            reason=health_result["reason"],
                            user_accepted="pending"
                        )
                        db.add(new_escalation)
                        db.commit()
                        
                        # Send SYSTEM_SUGGESTION
                        system_message = {
                            "type": "SYSTEM_SUGGESTION",
                            "session_id": session_id,
                            "message": "I want to make sure you get the best support. It might help to talk with a professional therapist. Would you like me to book an appointment for you?",
                            "reason": health_result["reason"]
                        }
                        await manager.broadcast_to_session(system_message, session_id)
                        
                        # 🛑 STOP HERE - Do NOT generate AI response
                        continue
                
                # ============================================
                # STEP 4: Generate normal AI response
                # ============================================
                # Only reach here if no escalation was triggered
                logger.info(f"=" * 80)
                logger.info(f"💬 GENERATING NORMAL AI RESPONSE")
                logger.info(f"Session: {session_id}")
                logger.info(f"User message: '{message_create.content[:50]}...'")
                logger.info(f"=" * 80)
                
                # Send typing indicator
                await manager.send_typing_indicator(session_id, "ai", True)
                
                # Generate AI response (with Gemini AI)
                ai_response_content = chat_service.get_ai_response(
                    message_create.content,
                    session_id=UUID(session_id),
                    db=db
                )
                logger.info(f"AI response generated: '{ai_response_content[:100]}...'")
                
                # 🚨 CRITICAL: Check if Gemini wants to escalate
                if "<<ESCALATE>>" in ai_response_content:
                    logger.warning(f"=" * 80)
                    logger.warning(f"🚨 GEMINI AI DETECTED ESCALATION NEED 🚨")
                    logger.warning(f"Session: {session_id}")
                    logger.warning(f"Gemini said: {ai_response_content}")
                    logger.warning(f"=" * 80)
                    
                    # Stop typing indicator
                    await manager.send_typing_indicator(session_id, "ai", False)
                    
                    # Create escalation record
                    gemini_escalation = ChatEscalation(
                        session_id=UUID(session_id),
                        reason="gemini_detected",
                        user_accepted="pending"
                    )
                    db.add(gemini_escalation)
                    db.commit()
                    logger.warning(f"✅ Created Gemini escalation record ID: {gemini_escalation.id}")
                    
                    # Send SYSTEM_SUGGESTION
                    system_message = {
                        "type": "SYSTEM_SUGGESTION",
                        "session_id": session_id,
                        "message": "I can help you connect with a therapist. Would you like me to book an appointment for you?",
                        "reason": "gemini_detected"
                    }
                    logger.warning(f"📤 Sending SYSTEM_SUGGESTION (Gemini escalation)")
                    await manager.broadcast_to_session(system_message, session_id)
                    logger.warning(f"🛑 SKIPPING AI RESPONSE - Gemini triggered escalation")
                    continue  # Skip sending the <<ESCALATE>> token as a message
                
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
                    "sender": "ai",  # Use "sender" not "sender_type"
                    "content": ai_message.content,
                    "emotion": ai_message.emotion,
                    "confidence": ai_message.confidence,
                    "created_at": ai_message.created_at.isoformat()
                }
                
                await manager.broadcast_to_session(ai_message_response, session_id)
                logger.info(f"✅ AI response broadcasted")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info(f"Client disconnected from session {session_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error in session {session_id}: {e}")
        manager.disconnect(websocket, session_id)
