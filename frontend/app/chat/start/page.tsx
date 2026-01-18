'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { chatApi } from '@/services/api'
import { useChatStore } from '@/store/chatStore'
import { MessageCircle, ArrowRight } from 'lucide-react'

export default function StartChatPage() {
  const [name, setName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const setSession = useChatStore((state) => state.setSession)

  const handleStartChat = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const session = await chatApi.createSession(name || undefined)
      setSession(session.session_id, session.visitor_id, session.visitor_name)
      router.push(`/chat/${session.session_id}`)
    } catch (error) {
      console.error('Failed to create chat session:', error)
      alert('Failed to start chat. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="card">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <MessageCircle className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Start Your Chat
            </h1>
            <p className="text-gray-600">
              You can optionally provide a name, or remain completely anonymous.
            </p>
          </div>

          <form onSubmit={handleStartChat} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Your Name (Optional)
              </label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Leave blank to stay anonymous"
                className="input-field"
                maxLength={50}
              />
              <p className="mt-2 text-xs text-gray-500">
                This is only for display purposes. No personal data is stored.
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <span>Creating session...</span>
              ) : (
                <>
                  <span>Start Chatting</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 p-4 bg-primary-50 rounded-lg">
            <p className="text-sm text-primary-900">
              <strong>Remember:</strong> You're safe here. Everything you share is confidential. 
              A therapist can join your chat if you need additional support.
            </p>
          </div>
        </div>

        <div className="text-center mt-6">
          <a href="/" className="text-primary-600 hover:text-primary-700 font-medium">
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  )
}
