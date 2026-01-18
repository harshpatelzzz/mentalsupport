from typing import Dict, List
from uuid import UUID
from fastapi import WebSocket
from app.core.logging import logger


class ConnectionManager:
    """
    Manages WebSocket connections for real-time chat.
    Handles connection lifecycle and message broadcasting.
    """
    
    def __init__(self):
        # Map of session_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Chat session identifier
        """
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected to session {session_id}. Total connections: {len(self.active_connections[session_id])}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Chat session identifier
        """
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
                logger.info(f"WebSocket disconnected from session {session_id}")
            
            # Clean up empty session lists
            if len(self.active_connections[session_id]) == 0:
                del self.active_connections[session_id]
    
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
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to session {session_id}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, session_id)
    
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
