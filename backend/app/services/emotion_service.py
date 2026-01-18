from typing import Optional, Tuple
from datetime import datetime
import re
from app.core.config import settings
from app.core.logging import logger


class EmotionAnalyzer:
    """
    Emotion analysis service using HuggingFace transformers with rule-based fallback.
    Analyzes text content and returns emotion classification with confidence score.
    """
    
    def __init__(self):
        self.model = None
        self.use_transformer = True
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the HuggingFace emotion classification model"""
        # For quick startup, use rule-based detection only
        # To enable HuggingFace transformer: install transformers and torch, then uncomment below
        logger.info("Using rule-based emotion detection for fast startup")
        self.use_transformer = False
        
        # Uncomment to enable HuggingFace transformer (requires torch & transformers installed):
        # try:
        #     from transformers import pipeline
        #     logger.info(f"Loading emotion model: {settings.EMOTION_MODEL}")
        #     self.model = pipeline(
        #         "text-classification",
        #         model=settings.EMOTION_MODEL,
        #         top_k=1
        #     )
        #     logger.info("Emotion model loaded successfully")
        #     self.use_transformer = True
        # except Exception as e:
        #     logger.warning(f"Failed to load transformer model: {e}. Using fallback emotion detection.")
        #     self.use_transformer = False
    
    def analyze(self, text: str) -> Tuple[str, float]:
        """
        Analyze emotion in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (emotion: str, confidence: float)
        """
        if not text or len(text.strip()) == 0:
            return "neutral", 0.5
        
        # Try transformer model first
        if self.use_transformer and self.model:
            try:
                result = self.model(text[:512])[0][0]  # Limit text length
                emotion = result['label'].lower()
                confidence = result['score']
                return emotion, confidence
            except Exception as e:
                logger.warning(f"Transformer analysis failed: {e}. Using fallback.")
        
        # Fallback to rule-based emotion detection
        return self._fallback_emotion_detection(text)
    
    def _fallback_emotion_detection(self, text: str) -> Tuple[str, float]:
        """
        Rule-based emotion detection using keyword matching.
        Returns emotion and confidence score.
        """
        text_lower = text.lower()
        
        # Emotion keyword dictionaries
        emotion_keywords = {
            "joy": ["happy", "excited", "great", "wonderful", "amazing", "fantastic", "love", "enjoy", "glad", "pleased"],
            "sadness": ["sad", "depressed", "unhappy", "miserable", "down", "lonely", "cry", "grief", "sorrow", "blue"],
            "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated", "rage", "hate", "upset"],
            "fear": ["afraid", "scared", "anxious", "worried", "nervous", "panic", "terrified", "frightened", "fear"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "unexpected", "wow", "incredible"],
            "disgust": ["disgusted", "gross", "awful", "terrible", "horrible", "nasty", "yuck"],
            "neutral": ["okay", "fine", "alright", "normal", "regular"]
        }
        
        # Count matches for each emotion
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                emotion_scores[emotion] = count
        
        # Return dominant emotion or neutral
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            # Calculate confidence based on keyword matches (normalize to 0.5-0.9 range)
            max_count = emotion_scores[dominant_emotion]
            confidence = min(0.5 + (max_count * 0.1), 0.9)
            return dominant_emotion, confidence
        
        return "neutral", 0.6


# Global emotion analyzer instance
emotion_analyzer = EmotionAnalyzer()
