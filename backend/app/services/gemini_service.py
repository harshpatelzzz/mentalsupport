"""
Google Gemini AI Service for Mental Health Chat Support

This service uses Gemini AI with a specialized system prompt to:
1. Provide empathetic mental health support
2. Detect when users need professional therapist intervention  
3. Output <<ESCALATE>> token when escalation is needed
"""

from typing import List, Optional
from app.core.config import settings
from app.core.logging import logger


class GeminiService:
    """
    Wrapper for Google Gemini AI with mental health support capabilities.
    """
    
    # System prompt that controls Gemini's behavior
    SYSTEM_PROMPT = """You are a mental health support assistant.

Rules you MUST follow:
- Be empathetic and human
- Never repeat the same question twice
- If the user asks for a therapist, appointment, or human help:
  respond ONLY with the word: <<ESCALATE>>
- If the user seems distressed or stuck:
  suggest speaking to a therapist gently
- Do NOT give medical advice
- Keep responses short and supportive (2-3 sentences max)

Examples:
User: "I need a therapist"
You: <<ESCALATE>>

User: "Can I talk to a human?"
You: <<ESCALATE>>

User: "I'm feeling really sad"
You: I hear that you're feeling sad. It's okay to feel this way. Would you like to talk about what's bothering you?

User: "Nothing is working for me"
You: I'm sorry you're going through a difficult time. It might help to speak with a professional therapist who can provide more support. Would that be helpful?
"""
    
    def __init__(self):
        """Initialize Gemini service"""
        self.model = None
        self.enabled = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Google Gemini AI model"""
        if not settings.USE_GEMINI:
            logger.info("Gemini AI is disabled in settings")
            return
        
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "":
            logger.warning("GEMINI_API_KEY not set - using fallback responses")
            return
        
        try:
            import google.generativeai as genai
            
            # Configure Gemini with API key
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Create model with system instruction
            self.model = genai.GenerativeModel(
                "gemini-pro",
                system_instruction=self.SYSTEM_PROMPT
            )
            
            self.enabled = True
            logger.info("✅ Gemini AI initialized successfully")
            
        except ImportError:
            logger.error("google-generativeai package not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
    
    def generate_response(self, conversation_history: List[dict]) -> str:
        """
        Generate AI response using Gemini.
        
        Args:
            conversation_history: List of {role: 'user'|'ai', content: str}
            
        Returns:
            AI response text (may contain <<ESCALATE>> token)
        """
        if not self.enabled or not self.model:
            logger.info("Gemini not enabled, using fallback")
            return self._fallback_response(conversation_history)
        
        try:
            # Format conversation for Gemini
            # Take last 6 messages (3 exchanges) for context
            recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
            
            # Build prompt from conversation
            prompt_parts = []
            for msg in recent_messages:
                role = "User" if msg.get("role") == "user" else "Assistant"
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            
            # Add current prompt
            prompt = "\n".join(prompt_parts)
            
            logger.info(f"Sending to Gemini:\n{prompt}")
            
            # Generate response
            response = self.model.generate_content(prompt)
            ai_text = response.text.strip()
            
            logger.info(f"Gemini response: {ai_text}")
            
            # Check if Gemini wants to escalate
            if "<<ESCALATE>>" in ai_text:
                logger.warning("🚨 Gemini detected need for therapist escalation!")
                logger.warning(f"Gemini's full response was: {ai_text}")
            
            return ai_text
            
        except Exception as e:
            logger.error(f"Gemini AI error: {e}")
            return self._fallback_response(conversation_history)
    
    def _fallback_response(self, conversation_history: List[dict]) -> str:
        """
        Simple fallback responses when Gemini is not available.
        Still includes <<ESCALATE>> token detection for keywords.
        """
        if not conversation_history:
            return "Hello! I'm here to listen and support you. How are you feeling today?"
        
        last_message = conversation_history[-1].get("content", "").lower()
        
        # Check for direct escalation keywords
        escalation_keywords = ["therapist", "counselor", "doctor", "appointment", "human", "real person"]
        if any(keyword in last_message for keyword in escalation_keywords):
            return "<<ESCALATE>>"
        
        # Generic supportive responses
        responses = [
            "I hear you. Can you tell me more about what you're experiencing?",
            "That sounds challenging. I'm here to listen.",
            "Thank you for sharing that with me. How does that make you feel?",
            "I understand. Would you like to talk more about this?",
        ]
        
        import random
        return random.choice(responses)
    
    def is_escalation_response(self, response: str) -> bool:
        """
        Check if AI response contains escalation token.
        
        Args:
            response: AI generated text
            
        Returns:
            True if response contains <<ESCALATE>>
        """
        return "<<ESCALATE>>" in response


# Global instance
gemini_service = GeminiService()
