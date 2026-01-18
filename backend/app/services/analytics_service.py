from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from collections import Counter

from app.models.chat import ChatMessage
from app.models.emotion import EmotionData
from app.models.appointment import Appointment, AppointmentStatus
from app.schemas.analytics import SessionStats, EmotionTrend, AnalyticsSummary


class AnalyticsService:
    """
    Service for generating analytics and insights.
    Provides statistics on sessions, emotions, and appointments.
    """
    
    @staticmethod
    def get_analytics_summary(db: Session, days: int = 30) -> AnalyticsSummary:
        """
        Generate comprehensive analytics summary.
        
        Args:
            db: Database session
            days: Number of days to analyze
            
        Returns:
            AnalyticsSummary with various metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Total sessions (unique session IDs)
        total_sessions = db.query(func.count(distinct(ChatMessage.session_id)))\
            .filter(ChatMessage.created_at >= cutoff_date)\
            .scalar() or 0
        
        # Total messages
        total_messages = db.query(func.count(ChatMessage.id))\
            .filter(ChatMessage.created_at >= cutoff_date)\
            .scalar() or 0
        
        # Sessions per day
        sessions_per_day = AnalyticsService._get_sessions_per_day(db, cutoff_date)
        
        # Emotion distribution
        emotion_distribution = AnalyticsService._get_emotion_distribution(db, cutoff_date)
        
        # Average chat duration
        avg_duration = AnalyticsService._get_average_chat_duration(db, cutoff_date)
        
        # Appointment completion rate
        completion_rate = AnalyticsService._get_appointment_completion_rate(db, cutoff_date)
        
        # Recent emotion trends
        emotion_trends = AnalyticsService._get_recent_emotion_trends(db, limit=100)
        
        return AnalyticsSummary(
            total_sessions=total_sessions,
            total_messages=total_messages,
            sessions_per_day=sessions_per_day,
            emotion_distribution=emotion_distribution,
            average_chat_duration=avg_duration,
            appointment_completion_rate=completion_rate,
            recent_emotion_trends=emotion_trends
        )
    
    @staticmethod
    def _get_sessions_per_day(db: Session, cutoff_date: datetime) -> Dict[str, int]:
        """Get session count grouped by day"""
        results = db.query(
            func.date(ChatMessage.created_at).label('date'),
            func.count(distinct(ChatMessage.session_id)).label('count')
        ).filter(
            ChatMessage.created_at >= cutoff_date
        ).group_by(
            func.date(ChatMessage.created_at)
        ).all()
        
        return {str(row.date): row.count for row in results}
    
    @staticmethod
    def _get_emotion_distribution(db: Session, cutoff_date: datetime) -> Dict[str, int]:
        """Get emotion count distribution"""
        results = db.query(
            EmotionData.emotion,
            func.count(EmotionData.id).label('count')
        ).filter(
            EmotionData.created_at >= cutoff_date
        ).group_by(
            EmotionData.emotion
        ).all()
        
        return {row.emotion: row.count for row in results}
    
    @staticmethod
    def _get_average_chat_duration(db: Session, cutoff_date: datetime) -> float:
        """Calculate average chat session duration in minutes"""
        # Get all unique sessions
        sessions = db.query(distinct(ChatMessage.session_id))\
            .filter(ChatMessage.created_at >= cutoff_date)\
            .all()
        
        if not sessions:
            return 0.0
        
        durations = []
        for (session_id,) in sessions:
            messages = db.query(ChatMessage)\
                .filter(ChatMessage.session_id == session_id)\
                .order_by(ChatMessage.created_at)\
                .all()
            
            if len(messages) >= 2:
                duration = (messages[-1].created_at - messages[0].created_at).total_seconds() / 60
                durations.append(duration)
        
        return round(sum(durations) / len(durations), 2) if durations else 0.0
    
    @staticmethod
    def _get_appointment_completion_rate(db: Session, cutoff_date: datetime) -> float:
        """Calculate appointment completion rate as percentage"""
        total = db.query(func.count(Appointment.id))\
            .filter(Appointment.created_at >= cutoff_date)\
            .scalar() or 0
        
        if total == 0:
            return 0.0
        
        completed = db.query(func.count(Appointment.id))\
            .filter(
                Appointment.created_at >= cutoff_date,
                Appointment.status == AppointmentStatus.COMPLETED
            ).scalar() or 0
        
        return round((completed / total) * 100, 2)
    
    @staticmethod
    def _get_recent_emotion_trends(db: Session, limit: int = 100) -> List[EmotionTrend]:
        """Get recent emotion trends for visualization"""
        emotion_data = db.query(EmotionData)\
            .order_by(EmotionData.created_at.desc())\
            .limit(limit)\
            .all()
        
        trends = [
            EmotionTrend(
                timestamp=ed.created_at,
                emotion=ed.emotion,
                confidence=ed.confidence,
                session_id=str(ed.session_id)
            )
            for ed in emotion_data
        ]
        
        return list(reversed(trends))  # Chronological order
    
    @staticmethod
    def get_session_emotion_timeline(
        db: Session,
        session_id: str
    ) -> List[EmotionTrend]:
        """Get emotion timeline for a specific session"""
        emotion_data = db.query(EmotionData)\
            .filter(EmotionData.session_id == session_id)\
            .order_by(EmotionData.created_at)\
            .all()
        
        return [
            EmotionTrend(
                timestamp=ed.created_at,
                emotion=ed.emotion,
                confidence=ed.confidence,
                session_id=str(ed.session_id)
            )
            for ed in emotion_data
        ]


analytics_service = AnalyticsService()
