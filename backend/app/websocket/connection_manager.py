from typing import Dict, List, Optional
from uuid import UUID
from fastapi import WebSocket
from app.core.logging import logger


class ConnectionInfo:
    """Stores connection metadata"""
    def __init__(self, websocket: WebSocket, role: str):
        self.websocket = websocket
        self.role = role  # "user" | "therapist"


class ConnectionManager:
    """
    Manages WebSocket connections for real-time chat.
    Handles connection lifecycle and message broadcasting.
    Stores role per connection for proper routing.
    """
    
    def __init__(self):
        # Map of session_id -> list of ConnectionInfo objects
        self.active_connections: Dict[str, List[ConnectionInfo]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, role: str):
        """
        Accept and register a new WebSocket connection with role.
        
        Args:
            websocket: WebSocket connection
            session_id: Chat session identifier
            role: "user" or "therapist"
        """
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        conn_info = ConnectionInfo(websocket, role)
        self.active_connections[session_id].append(conn_info)
        logger.warning(f"🔌 WebSocket connected to session {session_id} as '{role}'. Total connections: {len(self.active_connections[session_id])}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Chat session identifier
        """
        if session_id in self.active_connections:
            # Find and remove the connection
            for conn_info in self.active_connections[session_id]:
                if conn_info.websocket == websocket:
                    self.active_connections[session_id].remove(conn_info)
                    logger.info(f"🔌 WebSocket disconnected from session {session_id} (role: {conn_info.role})")
                    break
            
            # Clean up empty session lists
            if len(self.active_connections[session_id]) == 0:
                del self.active_connections[session_id]
    
    def get_role(self, websocket: WebSocket, session_id: str) -> Optional[str]:
        """
        Get the role for a specific websocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            
        Returns:
            Role ("user" or "therapist") or None if not found
        """
        if session_id in self.active_connections:
            for conn_info in self.active_connections[session_id]:
                if conn_info.websocket == websocket:
                    return conn_info.role
        return None
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            message: Message data (will be JSON serialized)
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_session(self, message: dict, session_id: str):
        """
        Broadcast a message to all connections in a session.
        
        Args:
            message: Message data (will be JSON serialized)
            session_id: Target session identifier
        """
        if session_id not in self.active_connections:
            logger.warning(f"No active connections for session {session_id}")
            return
        
        # Send to all connections in the session
        disconnected = []
        for conn_info in self.active_connections[session_id]:
            try:
                await conn_info.websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to session {session_id}: {e}")
                disconnected.append(conn_info.websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket, session_id)
    
    async def send_typing_indicator(self, session_id: str, sender_type: str, is_typing: bool):
        """
        Send typing indicator to session participants.
        
        Args:
            session_id: Target session
            sender_type: Who is typing (visitor/therapist/ai)
            is_typing: Whether typing started or stopped
        """
        message = {
            "type": "typing",
            "sender_type": sender_type,
            "is_typing": is_typing
        }
        await self.broadcast_to_session(message, session_id)
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of session IDs with active connections.
        
        Returns:
            List of active session IDs
        """
        return list(self.active_connections.keys())
    
    def get_connection_count(self, session_id: str) -> int:
        """
        Get number of active connections for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(session_id, []))


# Global connection manager instance
manager = ConnectionManager()
