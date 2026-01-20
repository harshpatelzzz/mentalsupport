"""
🚨 GLOBAL AI KILL SWITCH
=====================

Sessions in this set are FORBIDDEN from receiving AI responses.
Once a therapist connects, the session is added here FOREVER.

This is the SINGLE SOURCE OF TRUTH for AI disabling.
"""

# Session IDs where AI is PERMANENTLY DISABLED
AI_DISABLED_SESSIONS: set = set()


def disable_ai_for_session(session_id: str):
    """
    Permanently disable AI for this session.
    Called when therapist connects.
    
    Args:
        session_id: Session to disable AI for
    """
    AI_DISABLED_SESSIONS.add(session_id)


def is_ai_disabled(session_id: str) -> bool:
    """
    Check if AI is disabled for this session.
    
    Args:
        session_id: Session to check
        
    Returns:
        True if AI is disabled, False otherwise
    """
    return session_id in AI_DISABLED_SESSIONS


def enable_ai_for_session(session_id: str):
    """
    Re-enable AI for a session (for testing/admin purposes).
    
    Args:
        session_id: Session to enable AI for
    """
    AI_DISABLED_SESSIONS.discard(session_id)
