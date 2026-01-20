from fastapi import APIRouter, WebSocket
from typing import Dict, List
from datetime import datetime
import uuid

router = APIRouter()

human_connections: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/human-chat/{session_id}")
async def human_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(f"🧑‍⚕️ Human chat connection accepted for session {session_id}")

    human_connections.setdefault(session_id, []).append(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            print(f"📨 Human chat message received: {data}")

            message = {
                "type": "message",
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "sender": data["sender"],  # user | therapist
                "content": data["content"],
                "emotion": None,
                "confidence": None,
                "created_at": datetime.utcnow().isoformat()
            }

            # 🚨 ONLY BROADCAST — NO AI
            for ws in human_connections[session_id]:
                await ws.send_json(message)
            
            print(f"✅ Human chat message broadcasted to {len(human_connections[session_id])} connections")

    except Exception as e:
        print(f"❌ Human chat error: {e}")
        if session_id in human_connections:
            human_connections[session_id].remove(websocket)
