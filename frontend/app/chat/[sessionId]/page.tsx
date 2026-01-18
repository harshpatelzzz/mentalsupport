'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams } from 'next/navigation'
import { useChatStore } from '@/store/chatStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import { chatApi } from '@/services/api'
import { getEmotionColor, formatTime } from '@/lib/utils'
import { Send, Bot, User, Stethoscope, Circle } from 'lucide-react'

export default function ChatPage() {
  const params = useParams()
  const sessionId = params.sessionId as string
  
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  const {
    messages,
    setMessages,
    visitorId,
    visitorName,
    isConnected,
    isTherapistTyping,
    isAiTyping,
  } = useChatStore()
  
  const { sendMessage, sendTypingIndicator } = useWebSocket(sessionId)

  // Load chat history
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await chatApi.getChatHistory(sessionId)
        setMessages(history)
      } catch (error) {
        console.error('Failed to load chat history:', error)
      }
    }
    
    if (sessionId) {
      loadHistory()
    }
  }, [sessionId])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isAiTyping, isTherapistTyping])

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim() || !isConnected) return

    sendMessage(input, 'visitor', visitorId || undefined)
    setInput('')
    inputRef.current?.focus()
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
    
    // Send typing indicator (throttled in production)
    if (e.target.value.length > 0) {
      sendTypingIndicator(true, 'visitor')
    } else {
      sendTypingIndicator(false, 'visitor')
    }
  }

  const getSenderIcon = (senderType: string) => {
    switch (senderType) {
      case 'visitor':
        return <User className="w-5 h-5" />
      case 'therapist':
        return <Stethoscope className="w-5 h-5" />
      case 'ai':
        return <Bot className="w-5 h-5" />
      default:
        return <User className="w-5 h-5" />
    }
  }

  const getSenderLabel = (senderType: string) => {
    switch (senderType) {
      case 'visitor':
        return visitorName || 'You'
      case 'therapist':
        return 'Therapist'
      case 'ai':
        return 'AI Support'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-4 shadow-sm">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Support Chat</h1>
              <p className="text-sm text-gray-500">
                {isConnected ? 'Connected' : 'Connecting...'}
              </p>
            </div>
          </div>
          <a href="/" className="text-primary-600 hover:text-primary-700 font-medium text-sm">
            End Chat
          </a>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="container mx-auto max-w-4xl space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                Welcome to NeuroSupport
              </h3>
              <p className="text-gray-600">
                Start by sharing what's on your mind. We're here to listen.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender_type === 'visitor' ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div className={`flex space-x-3 max-w-2xl ${message.sender_type === 'visitor' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  message.sender_type === 'visitor' ? 'bg-primary-600 text-white' :
                  message.sender_type === 'therapist' ? 'bg-secondary-600 text-white' :
                  'bg-gray-600 text-white'
                }`}>
                  {getSenderIcon(message.sender_type)}
                </div>

                {/* Message Content */}
                <div className="flex-1">
                  <div className="flex items-baseline space-x-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      {getSenderLabel(message.sender_type)}
                    </span>
                    <span className="text-xs text-gray-500">
                      {formatTime(message.created_at)}
                    </span>
                  </div>

                  <div className={`message-bubble ${
                    message.sender_type === 'visitor' 
                      ? 'bg-primary-600 text-white' 
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>

                  {/* Emotion Badge */}
                  {message.emotion && message.confidence && (
                    <div className="mt-2">
                      <span className={`emotion-badge ${getEmotionColor(message.emotion)}`}>
                        {message.emotion} ({Math.round(message.confidence * 100)}%)
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicators */}
          {(isAiTyping || isTherapistTyping) && (
            <div className="flex justify-start animate-fade-in">
              <div className="flex space-x-3 max-w-2xl">
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  isTherapistTyping ? 'bg-secondary-600' : 'bg-gray-600'
                } text-white`}>
                  {isTherapistTyping ? <Stethoscope className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                </div>
                <div className="message-bubble bg-white border border-gray-200">
                  <div className="flex space-x-1">
                    <Circle className="w-2 h-2 fill-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <Circle className="w-2 h-2 fill-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <Circle className="w-2 h-2 fill-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-4 py-4 shadow-lg">
        <form onSubmit={handleSendMessage} className="container mx-auto max-w-4xl">
          <div className="flex space-x-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={handleInputChange}
              placeholder="Type your message..."
              className="input-field flex-1"
              disabled={!isConnected}
              maxLength={5000}
            />
            <button
              type="submit"
              disabled={!input.trim() || !isConnected}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="w-5 h-5" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
