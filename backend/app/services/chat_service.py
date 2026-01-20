from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from app.models.chat import ChatMessage, SenderType
from app.models.visitor import Visitor
from app.models.emotion import EmotionData
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services.emotion_service import emotion_analyzer
from app.services.gemini_service import gemini_service
from app.core.logging import logger
from app.core.ai_lock import is_ai_disabled


class ChatService:
    """
    Service layer for chat-related operations.
    Handles message persistence, emotion analysis, and chat history.
    """
    
    @staticmethod
    def create_message(
        db: Session,
        message_data: ChatMessageCreate
    ) -> ChatMessage:
        """
        Create a new chat message with emotion analysis.
        
        Args:
            db: Database session
            message_data: Message creation data
            
        Returns:
            Created ChatMessage instance
        """
        # Analyze emotion if message is from visitor
        emotion = None
        confidence = None
        
        if message_data.sender_type == SenderType.VISITOR:
            try:
                emotion, confidence = emotion_analyzer.analyze(message_data.content)
                logger.info(f"Emotion detected: {emotion} (confidence: {confidence:.2f})")
            except Exception as e:
                logger.error(f"Emotion analysis failed: {e}")
        
        # Create chat message
        chat_message = ChatMessage(
            session_id=message_data.session_id,
            visitor_id=message_data.visitor_id,
            sender_type=message_data.sender_type,
            content=message_data.content,
            emotion=emotion,
            confidence=confidence
        )
        
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        
        # Store emotion data separately for analytics
        if emotion and confidence:
            emotion_data = EmotionData(
                session_id=message_data.session_id,
                message_id=chat_message.id,
                emotion=emotion,
                confidence=confidence,
                message_content=message_data.content[:500]  # Store truncated content
            )
            db.add(emotion_data)
            db.commit()
        
        return chat_message
    
    @staticmethod
    def get_chat_history(
        db: Session,
        session_id: UUID,
        limit: int = 100
    ) -> List[ChatMessage]:
        """
        Retrieve chat history for a session.
        
        Args:
            db: Database session
            session_id: Chat session UUID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of ChatMessage instances
        """
        messages = db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at)\
            .limit(limit)\
            .all()
        
        return messages
    
    @staticmethod
    def get_ai_response(message_content: str, session_id: Optional[UUID] = None, db: Optional[Session] = None) -> str:
        """
        Generate AI chatbot response using Google Gemini AI.
        Falls back to simple responses if Gemini is not available.
        
        Args:
            message_content: User's message
            session_id: Chat session ID for conversation history (optional)
            db: Database session for retrieving history (optional)
            
        Returns:
            AI-generated response (may contain <<ESCALATE>> token)
        """
        # 🚨 GLOBAL AI KILL SWITCH - Check if AI is disabled for this session
        if session_id and is_ai_disabled(str(session_id)):
            logger.warning(f"☠️ AI DISABLED FOR SESSION {session_id} - RETURNING EMPTY RESPONSE")
            return ""  # AI IS DEAD - Return empty string
        
        # Build conversation history for context
        conversation_history = []
        
        if session_id and db:
            try:
                # Get recent messages for context
                recent_messages = ChatService.get_chat_history(db, session_id, limit=6)
                
                for msg in recent_messages:
                    role = "user" if msg.sender_type == SenderType.VISITOR else "ai"
                    conversation_history.append({
                        "role": role,
                        "content": msg.content
                    })
            except Exception as e:
                logger.warning(f"Could not load conversation history: {e}")
        
        # Add current user message
        conversation_history.append({
            "role": "user",
            "content": message_content
        })
        
        # Use Gemini AI to generate response
        try:
            ai_response = gemini_service.generate_response(conversation_history)
            logger.info(f"AI Response generated: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            # Fallback to simple response
            content_lower = message_content.lower()
            
            if any(word in content_lower for word in ["hello", "hi", "hey"]):
                return "Hello! I'm here to listen and support you. How are you feeling today?"
            elif any(word in content_lower for word in ["sad", "depressed", "down"]):
                return "I'm sorry you're feeling this way. It's okay to feel sad sometimes. Would you like to talk about what's troubling you?"
            elif any(word in content_lower for word in ["anxious", "worried", "nervous"]):
                return "I understand anxiety can be overwhelming. Let's take this one step at a time. What's causing you the most worry right now?"
            else:
                return "I hear you. Can you tell me more about how you're feeling?"
    
    @staticmethod
    def get_session_stats(db: Session, session_id: UUID) -> dict:
        """
        Get statistics for a chat session.
        
        Args:
            db: Database session
            session_id: Chat session UUID
            
        Returns:
            Dictionary with session statistics
        """
        messages = db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .all()
        
        if not messages:
            return {
                "message_count": 0,
                "start_time": None,
                "latest_time": None,
                "duration_minutes": 0
            }
        
        start_time = messages[0].created_at
        latest_time = messages[-1].created_at
        duration = (latest_time - start_time).total_seconds() / 60
        
        return {
            "message_count": len(messages),
            "start_time": start_time,
            "latest_time": latest_time,
            "duration_minutes": round(duration, 2)
        }


chat_service = ChatService()
