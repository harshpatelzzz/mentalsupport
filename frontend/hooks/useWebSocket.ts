import { useEffect, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import { useChatStore } from '@/store/chatStore'
import { ChatMessage } from '@/services/api'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

export function useWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null)
  const searchParams = useSearchParams()
  const {
    setWebSocket,
    setConnected,
    addMessage,
    setTherapistTyping,
    setAiTyping,
  } = useChatStore()

  useEffect(() => {
    if (!sessionId) return

    // 🚨 CRITICAL: Determine role from URL query params
    const isTherapist = searchParams.get('therapist') === 'true'
    const role = isTherapist ? 'therapist' : 'user'
    
    // Include role in WebSocket URL
    const ws = new WebSocket(`${WS_URL}/api/chat/ws/${sessionId}?role=${role}`)
    console.log(`🔌 Connecting WebSocket with role: ${role}`)

    ws.onopen = () => {
      console.log('WebSocket connected')
      setConnected(true)
      setWebSocket(ws)
      wsRef.current = ws
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('📥 WebSocket message received:', data.type, data)

      if (data.type === 'message') {
        // New message received
        const message: ChatMessage = {
          id: data.id,
          session_id: data.session_id,
          sender_type: data.sender || data.sender_type, // Handle both "sender" and legacy "sender_type"
          content: data.content,
          emotion: data.emotion,
          confidence: data.confidence,
          is_read: 'false',
          created_at: data.created_at,
        }
        addMessage(message)
      } else if (data.type === 'typing') {
        // Typing indicator
        const sender = data.sender || data.sender_type
        if (sender === 'therapist') {
          setTherapistTyping(data.is_typing)
        } else if (sender === 'ai') {
          setAiTyping(data.is_typing)
        }
      } else if (data.type === 'SYSTEM_SUGGESTION') {
        // System suggestion for escalation
        console.log('🚨 SYSTEM_SUGGESTION received:', data.message)
        console.log('🚨 Reason:', data.reason)
        
        // Trigger UI update via custom event
        window.dispatchEvent(new CustomEvent('escalation-suggestion', {
          detail: {
            message: data.message,
            reason: data.reason
          }
        }))
        console.log('✅ Dispatched escalation-suggestion event')
      } else if (data.type === 'ESCALATION_ACCEPTED') {
        // User accepted escalation
        console.log('✅ ESCALATION_ACCEPTED received')
        window.dispatchEvent(new CustomEvent('escalation-accepted', {
          detail: {
            message: data.message
          }
        }))
      } else if (data.type === 'SYSTEM_MESSAGE') {
        // System message (e.g., therapist joined)
        console.log('📢 SYSTEM_MESSAGE received:', data.message)
        // Add as a special system message to chat
        const systemMessage: ChatMessage = {
          id: 'system-' + Date.now(),
          session_id: data.session_id,
          sender_type: 'ai', // Display as system
          content: data.message,
          emotion: null,
          confidence: null,
          is_read: 'false',
          created_at: data.timestamp || new Date().toISOString(),
        }
        addMessage(systemMessage)
      } else {
        console.warn('⚠️ Unknown message type:', data.type)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setConnected(false)
      setWebSocket(null)
      wsRef.current = null
    }

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [sessionId])

  const sendMessage = (content: string, sender: string, visitorId?: string) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }

    ws.send(JSON.stringify({
      sender,  // "user" | "therapist" | "ai"
      content,
      visitor_id: visitorId,
    }))
  }

  const sendTypingIndicator = (isTyping: boolean, sender: string) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) return

    ws.send(JSON.stringify({
      type: 'typing',
      sender,  // "user" | "therapist" | "ai"
      is_typing: isTyping,
    }))
  }

  return {
    sendMessage,
    sendTypingIndicator,
  }
}
