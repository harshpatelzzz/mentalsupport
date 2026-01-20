'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import { useChatStore } from '@/store/chatStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import { chatApi } from '@/services/api'
import { getEmotionColor, formatTime } from '@/lib/utils'
import { Send, Bot, User, Stethoscope, Circle, AlertCircle, CheckCircle } from 'lucide-react'
import axios from 'axios'

export default function ChatPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const sessionId = params.sessionId as string
  const isTherapist = searchParams.get('therapist') === 'true'
  
  const [input, setInput] = useState('')
  const [showEscalation, setShowEscalation] = useState(false)
  const [escalationMessage, setEscalationMessage] = useState('')
  const [isBooking, setIsBooking] = useState(false)
  const [bookingConfirmed, setBookingConfirmed] = useState(false)
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

  // Therapist join appointment
  useEffect(() => {
    const joinAsTherapist = async () => {
      if (isTherapist && sessionId) {
        try {
          console.log('🧑‍⚕️ Therapist joining session:', sessionId)
          // Note: In real scenario, we'd get appointment_id from URL or API
          // For now, we'll fetch appointment by session_id first
          const appointmentsResponse = await axios.get(
            `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/appointments/session/${sessionId}`
          )
          if (appointmentsResponse.data) {
            const appointmentId = appointmentsResponse.data.id
            await chatApi.therapistJoinAppointment(appointmentId)
            console.log('✅ Therapist joined appointment successfully')
          }
        } catch (error) {
          console.error('Failed to join as therapist:', error)
        }
      }
    }
    
    joinAsTherapist()
  }, [isTherapist, sessionId])

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

  // Listen for escalation events
  useEffect(() => {
    console.log('🎧 Setting up escalation event listeners')
    
    const handleEscalationSuggestion = (event: any) => {
      console.log('🚨 escalation-suggestion event received!', event.detail)
      setEscalationMessage(event.detail.message)
      setShowEscalation(true)
      console.log('✅ Escalation UI state updated - should show amber alert')
    }

    const handleEscalationAccepted = (event: any) => {
      console.log('✅ escalation-accepted event received!')
      setShowEscalation(false)
      setBookingConfirmed(true)
    }

    window.addEventListener('escalation-suggestion', handleEscalationSuggestion)
    window.addEventListener('escalation-accepted', handleEscalationAccepted)
    
    console.log('✅ Event listeners attached')

    return () => {
      console.log('🧹 Cleaning up escalation event listeners')
      window.removeEventListener('escalation-suggestion', handleEscalationSuggestion)
      window.removeEventListener('escalation-accepted', handleEscalationAccepted)
    }
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isAiTyping, isTherapistTyping, showEscalation])

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim() || !isConnected) return

    const sender = isTherapist ? 'therapist' : 'user'  // "user" not "visitor"
    sendMessage(input, sender, visitorId || undefined)
    setInput('')
    inputRef.current?.focus()
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
    
    // Send typing indicator (throttled in production)
    const sender = isTherapist ? 'therapist' : 'user'  // "user" not "visitor"
    if (e.target.value.length > 0) {
      sendTypingIndicator(true, sender)
    } else {
      sendTypingIndicator(false, sender)
    }
  }

  const handleAcceptEscalation = async () => {
    if (isBooking) return // Prevent double-click
    
    setIsBooking(true)
    
    try {
      // Send acceptance message to trigger backend logic
      sendMessage('yes', 'user', visitorId || undefined)
      
      // Small delay to let backend process
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Call auto-book endpoint
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await axios.post(`${apiUrl}/api/appointments/auto-book`, {
        session_id: sessionId,
        visitor_id: visitorId,
        visitor_name: visitorName
      })
      
      // Hide escalation UI and show confirmation
      setShowEscalation(false)
      setBookingConfirmed(true)
      
      // Display appointment details as a chat message
      const confirmationMsg = response.data.message || 'Your appointment has been booked successfully!'
      console.log('Appointment booked:', response.data)
      
      // Confirmation will stay visible for user to see
      setTimeout(() => {
        setBookingConfirmed(false)
      }, 10000) // Hide after 10 seconds
      
    } catch (error) {
      console.error('Failed to book appointment:', error)
      alert('Failed to book appointment. Please try again.')
      setShowEscalation(true) // Show escalation UI again on error
    } finally {
      setIsBooking(false)
    }
  }

  const handleDeclineEscalation = () => {
    // Send decline message
    sendMessage('not now', 'user', visitorId || undefined)
    setShowEscalation(false)
    // Allow chat to continue normally
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
        <div className="container mx-auto max-w-4xl">
          {/* Escalation Prompt */}
          {showEscalation && !bookingConfirmed && (
            <div className="mb-4 bg-amber-50 border border-amber-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <p className="text-gray-900 mb-3">{escalationMessage}</p>
                  <div className="flex space-x-3">
                    <button
                      onClick={handleAcceptEscalation}
                      disabled={isBooking}
                      className="btn-primary flex items-center space-x-2 text-sm"
                    >
                      {isBooking ? (
                        <>
                          <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                          <span>Booking...</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle className="w-4 h-4" />
                          <span>Yes, book appointment</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleDeclineEscalation}
                      disabled={isBooking}
                      className="btn-outline text-sm"
                    >
                      Not now
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Booking Confirmed Message */}
          {bookingConfirmed && (
            <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <p className="text-green-900 font-medium">
                  Your appointment has been booked! A therapist will join this chat at the scheduled time.
                </p>
              </div>
            </div>
          )}

          {/* Regular Input Form */}
          {!showEscalation && (
            <form onSubmit={handleSendMessage}>
              <div className="flex space-x-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={handleInputChange}
                  placeholder="Type your message..."
                  className="input-field flex-1"
                  disabled={!isConnected || isBooking || bookingConfirmed}
                  maxLength={5000}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || !isConnected || isBooking || bookingConfirmed}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Send className="w-5 h-5" />
                  <span className="hidden sm:inline">Send</span>
                </button>
              </div>
            </form>
          )}
          
          {/* Placeholder when escalation is showing */}
          {showEscalation && (
            <div className="text-center text-gray-500 py-3">
              Please respond to the suggestion above
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
