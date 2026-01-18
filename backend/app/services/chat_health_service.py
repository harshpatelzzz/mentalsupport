from typing import List, Dict
from app.models.chat import ChatMessage, SenderType
from app.core.logging import logger


class ChatHealthService:
    """
    Service to evaluate chat session health and detect when escalation is needed.
    Analyzes message patterns to determine if a user needs professional help.
    """
    
    # Emotions that indicate distress
    NEGATIVE_EMOTIONS = ["sadness", "fear", "anger", "anxiety"]
    
    # AI confidence threshold below which we consider the bot ineffective
    LOW_CONFIDENCE_THRESHOLD = 0.55
    
    # Keywords that indicate user wants human therapist
    INTENT_KEYWORDS = [
        "therapist", "human", "real person", "appointment", "book", "someone", 
        "professional", "doctor", "counselor", "help me please", "talk to someone",
        "speak to someone", "need help", "schedule", "meet with"
    ]
    
    @staticmethod
    def has_direct_escalation_intent(text: str) -> bool:
        """
        STRICT check if user message explicitly requests therapist/appointment.
        This function is called IMMEDIATELY after user message is received.
        
        Args:
            text: The user's message text
            
        Returns:
            True if user is asking for therapist/appointment (triggers IMMEDIATE escalation)
        """
        if not text or len(text.strip()) == 0:
            return False
        
        content_lower = text.lower().strip()
        
        # Check each keyword
        for keyword in ChatHealthService.INTENT_KEYWORDS:
            if keyword in content_lower:
                logger.warning(f"🚨 DIRECT ESCALATION INTENT DETECTED: keyword '{keyword}' in message")
                logger.warning(f"Message: '{text[:100]}'")
                return True
        
        return False
    
    @staticmethod
    def check_user_intent(message_content: str) -> bool:
        """
        Alias for has_direct_escalation_intent for backwards compatibility.
        
        Args:
            message_content: The user's message text
            
        Returns:
            True if user is asking for therapist/appointment
        """
        return ChatHealthService.has_direct_escalation_intent(message_content)
    
    @staticmethod
    def detect_ai_repetition(messages: List[ChatMessage]) -> bool:
        """
        Detect if AI is repeating the same response (looping).
        
        Args:
            messages: List of recent chat messages
            
        Returns:
            True if AI is repeating responses
        """
        if not messages or len(messages) < 3:
            return False
        
        # Get AI messages from recent history
        ai_messages = [msg for msg in messages[-10:] if msg.sender_type == SenderType.AI]
        
        if len(ai_messages) < 3:
            return False
        
        # Check if any response appears 3+ times
        response_counts = {}
        for msg in ai_messages:
            # Normalize content (strip, lowercase, first 100 chars for comparison)
            normalized = msg.content.strip().lower()[:100]
            response_counts[normalized] = response_counts.get(normalized, 0) + 1
            
            if response_counts[normalized] >= 3:
                logger.warning(f"AI repetition detected: same response appeared {response_counts[normalized]} times")
                return True
        
        return False
    
    @staticmethod
    def evaluate_chat_health(messages: List[ChatMessage]) -> Dict:
        """
        Evaluate if a chat session is struggling and needs therapist intervention.
        Uses OR logic: triggers if ANY condition is met.
        
        Args:
            messages: List of recent chat messages (should be last 5-10)
            
        Returns:
            Dictionary with 'struggling' boolean and 'reason' string
        """
        if not messages or len(messages) < 2:
            # Not enough data to evaluate
            return {
                "struggling": False,
                "reason": None
            }
        
        # Check for AI repetition/looping FIRST
        if ChatHealthService.detect_ai_repetition(messages):
            return {
                "struggling": True,
                "reason": "ai_repetition"
            }
        
        # Look at last 5 messages for evaluation
        recent_messages = messages[-5:] if len(messages) >= 5 else messages
        
        # Count negative emotions in visitor messages
        negative_emotion_count = 0
        
        # Count low-confidence AI messages
        low_confidence_ai_count = 0
        
        for message in recent_messages:
            # Check visitor messages for negative emotions
            if message.sender_type == SenderType.VISITOR and message.emotion:
                if message.emotion.lower() in ChatHealthService.NEGATIVE_EMOTIONS:
                    negative_emotion_count += 1
                    logger.info(f"Detected negative emotion: {message.emotion}")
            
            # Check AI messages for low confidence
            if message.sender_type == SenderType.AI and message.confidence:
                if message.confidence < ChatHealthService.LOW_CONFIDENCE_THRESHOLD:
                    low_confidence_ai_count += 1
                    logger.info(f"Detected low AI confidence: {message.confidence}")
        
        # Evaluate if struggling based on ANY criteria (OR logic)
        emotional_distress = negative_emotion_count >= 3
        low_ai_effectiveness = low_confidence_ai_count >= 2
        
        if emotional_distress:
            logger.warning(f"Chat health check: Emotional distress detected ({negative_emotion_count} negative emotions)")
            return {
                "struggling": True,
                "reason": "emotional_distress"
            }
        
        if low_ai_effectiveness:
            logger.warning(f"Chat health check: Low AI effectiveness ({low_confidence_ai_count} low confidence responses)")
            return {
                "struggling": True,
                "reason": "low_ai_confidence"
            }
        
        # Chat is healthy
        return {
            "struggling": False,
            "reason": None
        }
    
    @staticmethod
    def should_trigger_escalation(
        messages: List[ChatMessage],
        escalation_already_triggered: bool
    ) -> bool:
        """
        Determine if escalation should be triggered for this session.
        
        Args:
            messages: Recent chat messages
            escalation_already_triggered: Whether escalation was already suggested
            
        Returns:
            Boolean indicating if escalation should be triggered
        """
        if escalation_already_triggered:
            # Only trigger once per session
            return False
        
        health_check = ChatHealthService.evaluate_chat_health(messages)
        return health_check["struggling"]


# Global instance
chat_health_service = ChatHealthService()
