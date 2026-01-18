'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { appointmentsApi } from '@/services/api'
import { Calendar, ArrowRight, CheckCircle } from 'lucide-react'

export default function BookAppointmentPage() {
  const [name, setName] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [appointmentId, setAppointmentId] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!date || !time) {
      alert('Please select a date and time')
      return
    }

    setIsLoading(true)

    try {
      // Combine date and time
      const startTime = new Date(`${date}T${time}`)
      
      const appointment = await appointmentsApi.create({
        visitor_name: name || undefined,
        start_time: startTime.toISOString(),
      })

      setAppointmentId(appointment.id)
      setSessionId(appointment.session_id)
    } catch (error) {
      console.error('Failed to create appointment:', error)
      alert('Failed to book appointment. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  if (appointmentId && sessionId) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-secondary-50 to-primary-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <div className="card text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              Appointment Booked!
            </h1>
            
            <p className="text-gray-600 mb-6">
              Your appointment has been scheduled successfully. You can start chatting now or wait until your appointment time.
            </p>

            <div className="bg-gray-50 rounded-lg p-4 mb-6 text-left">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="font-medium">Appointment ID:</span>
                  <span className="text-gray-600 font-mono">{appointmentId.slice(0, 8)}...</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Session ID:</span>
                  <span className="text-gray-600 font-mono">{sessionId.slice(0, 8)}...</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Date:</span>
                  <span className="text-gray-600">{date}</span>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Time:</span>
                  <span className="text-gray-600">{time}</span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => router.push(`/chat/${sessionId}`)}
                className="w-full btn-primary"
              >
                Start Chatting Now
              </button>
              
              <a href="/" className="block w-full btn-outline">
                Back to Home
              </a>
            </div>

            <p className="mt-6 text-sm text-gray-500">
              Save your Session ID to return to this chat later.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-50 to-primary-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="card">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-secondary-100 rounded-full mb-4">
              <Calendar className="w-8 h-8 text-secondary-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Book an Appointment
            </h1>
            <p className="text-gray-600">
              Schedule a session with a professional therapist
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
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
            </div>

            <div>
              <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Date *
              </label>
              <input
                type="date"
                id="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="input-field"
                required
              />
            </div>

            <div>
              <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Time *
              </label>
              <input
                type="time"
                id="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                className="input-field"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-secondary flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <span>Booking...</span>
              ) : (
                <>
                  <span>Book Appointment</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 p-4 bg-secondary-50 rounded-lg">
            <p className="text-sm text-secondary-900">
              <strong>Note:</strong> A chat session will be automatically created with your appointment. 
              You can start chatting anytime before your scheduled session.
            </p>
          </div>
        </div>

        <div className="text-center mt-6">
          <a href="/" className="text-secondary-600 hover:text-secondary-700 font-medium">
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  )
}
