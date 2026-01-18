import { create } from 'zustand'
import { ChatMessage } from '@/services/api'

interface ChatState {
  // Session data
  sessionId: string | null
  visitorId: string | null
  visitorName: string | null
  
  // Messages
  messages: ChatMessage[]
  
  // WebSocket
  ws: WebSocket | null
  isConnected: boolean
  
  // Typing indicators
  isTherapistTyping: boolean
  isAiTyping: boolean
  
  // Actions
  setSession: (sessionId: string, visitorId: string, visitorName?: string) => void
  addMessage: (message: ChatMessage) => void
  setMessages: (messages: ChatMessage[]) => void
  setWebSocket: (ws: WebSocket | null) => void
  setConnected: (connected: boolean) => void
  setTherapistTyping: (typing: boolean) => void
  setAiTyping: (typing: boolean) => void
  clearSession: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  // Initial state
  sessionId: null,
  visitorId: null,
  visitorName: null,
  messages: [],
  ws: null,
  isConnected: false,
  isTherapistTyping: false,
  isAiTyping: false,
  
  // Actions
  setSession: (sessionId, visitorId, visitorName) => 
    set({ sessionId, visitorId, visitorName }),
  
  addMessage: (message) => 
    set((state) => ({ messages: [...state.messages, message] })),
  
  setMessages: (messages) => 
    set({ messages }),
  
  setWebSocket: (ws) => 
    set({ ws }),
  
  setConnected: (connected) => 
    set({ isConnected: connected }),
  
  setTherapistTyping: (typing) => 
    set({ isTherapistTyping: typing }),
  
  setAiTyping: (typing) => 
    set({ isAiTyping: typing }),
  
  clearSession: () => 
    set({
      sessionId: null,
      visitorId: null,
      visitorName: null,
      messages: [],
      ws: null,
      isConnected: false,
      isTherapistTyping: false,
      isAiTyping: false,
    }),
}))
