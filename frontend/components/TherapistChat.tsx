"use client";
import { useEffect, useState } from "react";

interface Message {
  sender: string;
  content: string;
}

interface TherapistChatProps {
  sessionId: string;
}

export default function TherapistChat({ sessionId }: TherapistChatProps) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    const socket = new WebSocket(
      `ws://localhost:8000/ws/human-chat/${sessionId}`
    );

    socket.onmessage = (e) => {
      setMessages((m) => [...m, JSON.parse(e.data)]);
    };

    socket.onopen = () => {
      console.log("🧑‍⚕️ Therapist connected to human-chat");
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    setWs(socket);
    return () => socket.close();
  }, [sessionId]);

  const send = (text: string) => {
    if (!text.trim() || !ws) return;
    
    ws.send(JSON.stringify({
      sender: "therapist",
      content: text
    }));
    
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.sender === "therapist" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                m.sender === "therapist"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-900"
              }`}
            >
              <div className="text-xs font-semibold mb-1">
                {m.sender === "therapist" ? "You" : "User"}
              </div>
              <div>{m.content}</div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && send(input)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => send(input)}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
