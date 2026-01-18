import { useEffect, useRef } from 'react'
import { useChatStore } from '@/store/chatStore'
import { ChatMessage } from '@/services/api'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

export function useWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null)
  const {
    setWebSocket,
    setConnected,
    addMessage,
    setTherapistTyping,
    setAiTyping,
  } = useChatStore()

  useEffect(() => {
    if (!sessionId) return

    const ws = new WebSocket(`${WS_URL}/api/chat/ws/${sessionId}`)

    ws.onopen = () => {
      console.log('WebSocket connected')
      setConnected(true)
      setWebSocket(ws)
      wsRef.current = ws
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'message') {
        // New message received
        const message: ChatMessage = {
          id: data.id,
          session_id: data.session_id,
          sender_type: data.sender_type,
          content: data.content,
          emotion: data.emotion,
          confidence: data.confidence,
          is_read: 'false',
          created_at: data.created_at,
        }
        addMessage(message)
      } else if (data.type === 'typing') {
        // Typing indicator
        if (data.sender_type === 'therapist') {
          setTherapistTyping(data.is_typing)
        } else if (data.sender_type === 'ai') {
          setAiTyping(data.is_typing)
        }
      } else if (data.type === 'SYSTEM_SUGGESTION') {
        // System suggestion for escalation
        // Trigger UI update via custom event
        window.dispatchEvent(new CustomEvent('escalation-suggestion', {
          detail: {
            message: data.message,
            reason: data.reason
          }
        }))
      } else if (data.type === 'ESCALATION_ACCEPTED') {
        // User accepted escalation
        window.dispatchEvent(new CustomEvent('escalation-accepted', {
          detail: {
            message: data.message
          }
        }))
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

  const sendMessage = (content: string, senderType: string, visitorId?: string) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }

    ws.send(JSON.stringify({
      content,
      sender_type: senderType,
      visitor_id: visitorId,
    }))
  }

  const sendTypingIndicator = (isTyping: boolean, senderType: string) => {
    const ws = wsRef.current
    if (!ws || ws.readyState !== WebSocket.OPEN) return

    ws.send(JSON.stringify({
      type: 'typing',
      sender_type: senderType,
      is_typing: isTyping,
    }))
  }

  return {
    sendMessage,
    sendTypingIndicator,
  }
}
