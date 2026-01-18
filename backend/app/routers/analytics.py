from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import AnalyticsSummary
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics summary.
    Includes sessions, emotions, appointments, and trends.
    
    Args:
        days: Number of days to analyze (default: 30)
    """
    summary = analytics_service.get_analytics_summary(db, days)
    return summary


@router.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "NeuroSupport Analytics"
    }
