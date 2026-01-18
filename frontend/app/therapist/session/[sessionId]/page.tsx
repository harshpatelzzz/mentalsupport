'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { therapistApi, chatApi, appointmentsApi } from '@/services/api'
import Link from 'next/link'
import { ArrowLeft, MessageCircle, Save } from 'lucide-react'
import { Line } from 'react-chartjs-2'
import { getEmotionColor, formatDateTime } from '@/lib/utils'

export default function SessionDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params.sessionId as string
  const queryClient = useQueryClient()
  
  const [noteText, setNoteText] = useState('')
  const [appointmentId, setAppointmentId] = useState<string | null>(null)

  // Fetch appointment by session
  const { data: appointment } = useQuery({
    queryKey: ['appointment-session', sessionId],
    queryFn: () => appointmentsApi.getBySession(sessionId),
  })

  // Set appointment ID when data is fetched
  useEffect(() => {
    if (appointment) {
      setAppointmentId(appointment.id)
    }
  }, [appointment])

  // Fetch emotion timeline
  const { data: emotionTimeline } = useQuery({
    queryKey: ['emotion-timeline', sessionId],
    queryFn: () => therapistApi.getEmotionTimeline(sessionId),
  })

  // Fetch session stats
  const { data: sessionStats } = useQuery({
    queryKey: ['session-stats', sessionId],
    queryFn: () => chatApi.getSessionStats(sessionId),
  })

  // Fetch notes
  const { data: notes } = useQuery({
    queryKey: ['therapist-notes', appointmentId],
    queryFn: () => therapistApi.getAppointmentNotes(appointmentId!),
    enabled: !!appointmentId,
  })

  // Create note mutation
  const createNoteMutation = useMutation({
    mutationFn: (note: string) => 
      therapistApi.createNote({ appointment_id: appointmentId!, note }),
    onSuccess: () => {
      setNoteText('')
      queryClient.invalidateQueries({ queryKey: ['therapist-notes', appointmentId] })
    },
  })

  const handleSaveNote = () => {
    if (!noteText.trim() || !appointmentId) return
    createNoteMutation.mutate(noteText)
  }

  // Prepare emotion timeline chart
  const emotionChartData = emotionTimeline ? {
    labels: emotionTimeline.map(e => 
      new Date(e.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    ),
    datasets: [
      {
        label: 'Emotion Confidence',
        data: emotionTimeline.map(e => e.confidence),
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.5)',
        tension: 0.3,
      },
    ],
  } : null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/therapist" className="text-primary-600 hover:text-primary-700">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Session Details</h1>
                <p className="text-sm text-gray-600 font-mono">{sessionId}</p>
              </div>
            </div>
            <button
              onClick={() => router.push(`/chat/${sessionId}`)}
              className="btn-primary flex items-center space-x-2"
            >
              <MessageCircle className="w-5 h-5" />
              <span>Join Chat</span>
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Session Stats */}
            {sessionStats && (
              <div className="card">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Session Statistics</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Message Count</p>
                    <p className="text-2xl font-bold text-gray-900">{sessionStats.message_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Duration</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {sessionStats.duration_minutes.toFixed(1)} min
                    </p>
                  </div>
                  {sessionStats.start_time && (
                    <div>
                      <p className="text-sm text-gray-600">Started</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {formatDateTime(sessionStats.start_time)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Emotion Timeline Chart */}
            {emotionTimeline && emotionTimeline.length > 0 && (
              <div className="card">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Emotion Timeline</h2>
                <div className="h-64 mb-6">
                  {emotionChartData && (
                    <Line
                      data={emotionChartData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                          y: {
                            beginAtZero: true,
                            max: 1,
                            ticks: {
                              callback: (value) => `${(Number(value) * 100).toFixed(0)}%`,
                            },
                          },
                        },
                      }}
                    />
                  )}
                </div>
                
                {/* Emotion List */}
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Detected Emotions</h3>
                  <div className="flex flex-wrap gap-2">
                    {emotionTimeline.map((e, index) => (
                      <span
                        key={index}
                        className={`emotion-badge ${getEmotionColor(e.emotion)}`}
                      >
                        {e.emotion} ({Math.round(e.confidence * 100)}%)
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Appointment Info */}
            {appointment && (
              <div className="card">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Appointment Information</h2>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Visitor</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {appointment.visitor_name || 'Anonymous'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Scheduled Time</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatDateTime(appointment.start_time)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <span className={`emotion-badge ${
                      appointment.status === 'completed' ? 'bg-green-200 text-green-800' :
                      appointment.status === 'scheduled' ? 'bg-yellow-200 text-yellow-800' :
                      'bg-red-200 text-red-800'
                    }`}>
                      {appointment.status}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar - Notes */}
          <div className="space-y-6">
            {/* Create Note */}
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Private Notes</h2>
              <p className="text-sm text-gray-600 mb-4">
                These notes are private and not visible to the visitor.
              </p>
              
              <textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                placeholder="Write your session notes here..."
                className="input-field min-h-[200px] resize-y"
                maxLength={10000}
              />
              
              <button
                onClick={handleSaveNote}
                disabled={!noteText.trim() || !appointmentId || createNoteMutation.isPending}
                className="w-full btn-primary mt-4 flex items-center justify-center space-x-2"
              >
                <Save className="w-5 h-5" />
                <span>{createNoteMutation.isPending ? 'Saving...' : 'Save Note'}</span>
              </button>
            </div>

            {/* Previous Notes */}
            {notes && notes.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Previous Notes</h3>
                <div className="space-y-4 max-h-[500px] overflow-y-auto">
                  {notes.map((note: any) => (
                    <div key={note.id} className="border-l-4 border-primary-500 pl-4 py-2">
                      <p className="text-sm text-gray-600 mb-1">
                        {formatDateTime(note.created_at)}
                      </p>
                      <p className="text-gray-900 whitespace-pre-wrap">{note.note}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
