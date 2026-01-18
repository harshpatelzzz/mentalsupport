from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class EmotionTrend(BaseModel):
    """Emotion data point for trend charts"""
    timestamp: datetime
    emotion: str
    confidence: float
    session_id: str


class SessionStats(BaseModel):
    """Statistics for a single session"""
    session_id: str
    message_count: int
    duration_minutes: float
    dominant_emotion: str
    start_time: datetime


class AnalyticsSummary(BaseModel):
    """Overall analytics summary"""
    total_sessions: int
    total_messages: int
    sessions_per_day: Dict[str, int]
    emotion_distribution: Dict[str, int]
    average_chat_duration: float
    appointment_completion_rate: float
    recent_emotion_trends: List[EmotionTrend]
