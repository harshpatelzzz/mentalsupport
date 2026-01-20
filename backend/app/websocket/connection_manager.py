from typing import Dict, Optional
from fastapi import WebSocket
from app.core.logging import logger


class ConnectionManager:
    """
    NUCLEAR FIX: Manages WebSocket connections with hard therapist detection.
    If therapist socket exists → AI code path is UNREACHABLE.
    """
    
    def __init__(self):
        # session_id -> {"user": WebSocket, "therapist": WebSocket}
        self.sessions: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, session_id: str, role: str, websocket: WebSocket):
        """
        Connect a websocket with role.
        
        Args:
            session_id: Chat session identifier
            role: "user" or "therapist"
            websocket: WebSocket connection
        """
        await websocket.accept()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        
        self.sessions[session_id][role] = websocket
        logger.warning(f"🔌 WebSocket connected to session {session_id} as '{role}'. Active roles: {list(self.sessions[session_id].keys())}")
    
    def disconnect(self, session_id: str, role: str):
        """
        Disconnect a role from a session.
        
        Args:
            session_id: Chat session identifier
            role: Role to disconnect
        """
        if session_id in self.sessions:
            removed = self.sessions[session_id].pop(role, None)
            if removed:
                logger.warning(f"🔌 WebSocket disconnected from session {session_id} (role: {role})")
            
            # Clean up empty sessions
            if len(self.sessions[session_id]) == 0:
                del self.sessions[session_id]
    
    def has_therapist(self, session_id: str) -> bool:
        """
        🚨 NUCLEAR CHECK: Does this session have a therapist connected?
        
        This is the SINGLE SOURCE OF TRUTH for bot disabling.
        If this returns True, AI code path is UNREACHABLE.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if therapist socket exists, False otherwise
        """
        return (
            session_id in self.sessions and
            "therapist" in self.sessions[session_id]
        )
    
    def get_role(self, websocket: WebSocket, session_id: str) -> Optional[str]:
        """
        Get the role for a specific websocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            
        Returns:
            Role ("user" or "therapist") or None if not found
        """
        if session_id in self.sessions:
            for role, ws in self.sessions[session_id].items():
                if ws == websocket:
                    return role
        return None
    
    async def send_to_role(self, session_id: str, role: str, message: dict):
        """
        Send a message to a specific role in a session.
        
        Args:
            session_id: Session identifier
            role: Target role ("user" or "therapist")
            message: Message data (will be JSON serialized)
        """
        if session_id in self.sessions and role in self.sessions[session_id]:
            try:
                await self.sessions[session_id][role].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {role} in session {session_id}: {e}")
                self.disconnect(session_id, role)
    
    async def send_to_other(self, session_id: str, sender_role: str, message: dict):
        """
        Send a message to all OTHER roles in a session (not the sender).
        
        Args:
            session_id: Session identifier
            sender_role: Role of the sender (will be excluded)
            message: Message data (will be JSON serialized)
        """
        if session_id not in self.sessions:
            logger.warning(f"No active connections for session {session_id}")
            return
        
        disconnected = []
        for role, ws in self.sessions[session_id].items():
            if role != sender_role:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to {role} in session {session_id}: {e}")
                    disconnected.append(role)
        
        # Clean up disconnected
        for role in disconnected:
            self.disconnect(session_id, role)
    
    async def broadcast_to_session(self, message: dict, session_id: str):
        """
        Broadcast a message to ALL connections in a session.
        
        Args:
            message: Message data (will be JSON serialized)
            session_id: Target session identifier
        """
        if session_id not in self.sessions:
            logger.warning(f"No active connections for session {session_id}")
            return
        
        disconnected = []
        for role, ws in self.sessions[session_id].items():
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {role} in session {session_id}: {e}")
                disconnected.append(role)
        
        # Clean up disconnected
        for role in disconnected:
            self.disconnect(session_id, role)
    
    async def send_typing_indicator(self, session_id: str, sender_role: str, is_typing: bool):
        """
        Send typing indicator to OTHER participants in session.
        
        Args:
            session_id: Target session
            sender_role: Who is typing ("user" or "therapist")
            is_typing: Whether typing started or stopped
        """
        message = {
            "type": "typing",
            "sender": sender_role,
            "is_typing": is_typing
        }
        await self.send_to_other(session_id, sender_role, message)
    
    def get_active_sessions(self) -> list:
        """
        Get list of session IDs with active connections.
        
        Returns:
            List of active session IDs
        """
        return list(self.sessions.keys())
    
    def get_connection_count(self, session_id: str) -> int:
        """
        Get number of active connections for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of active connections
        """
        return len(self.sessions.get(session_id, {}))


# Global connection manager instance
manager = ConnectionManager()
