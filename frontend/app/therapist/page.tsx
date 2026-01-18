'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { appointmentsApi, therapistApi } from '@/services/api'
import { useRouter } from 'next/navigation'
import { Calendar, MessageCircle, TrendingUp, Users, Clock, CheckCircle, XCircle, Circle as CircleIcon } from 'lucide-react'
import Link from 'next/link'
import { formatDateTime } from '@/lib/utils'

export default function TherapistDashboard() {
  const router = useRouter()
  const [selectedTab, setSelectedTab] = useState<'appointments' | 'active'>('appointments')

  // Fetch appointments
  const { data: appointments, isLoading: appointmentsLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: () => appointmentsApi.getAll(),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  // Fetch active sessions
  const { data: activeSessions, isLoading: activeLoading } = useQuery({
    queryKey: ['active-sessions'],
    queryFn: () => therapistApi.getActiveSessions(),
    refetchInterval: 3000, // Refresh every 3 seconds
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'scheduled':
        return <Clock className="w-5 h-5 text-yellow-600" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <CircleIcon className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Therapist Dashboard</h1>
              <p className="text-gray-600 mt-1">Manage appointments and join active sessions</p>
            </div>
            <div className="flex space-x-4">
              <Link href="/therapist/analytics" className="btn-outline flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Analytics</span>
              </Link>
              <Link href="/" className="text-primary-600 hover:text-primary-700 font-medium">
                Home
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Appointments</p>
                <p className="text-3xl font-bold text-gray-900">
                  {appointments?.length || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                <Calendar className="w-6 h-6 text-primary-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Active Sessions</p>
                <p className="text-3xl font-bold text-gray-900">
                  {activeSessions?.count || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <Users className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Scheduled Today</p>
                <p className="text-3xl font-bold text-gray-900">
                  {appointments?.filter(a => {
                    const today = new Date().toDateString()
                    const apptDate = new Date(a.start_time).toDateString()
                    return today === apptDate && a.status === 'scheduled'
                  }).length || 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-secondary-100 rounded-full flex items-center justify-center">
                <Clock className="w-6 h-6 text-secondary-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setSelectedTab('appointments')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedTab === 'appointments'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                All Appointments
              </button>
              <button
                onClick={() => setSelectedTab('active')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  selectedTab === 'active'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Active Sessions
                {activeSessions?.count > 0 && (
                  <span className="ml-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                    {activeSessions.count}
                  </span>
                )}
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        {selectedTab === 'appointments' && (
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Appointments</h2>
            
            {appointmentsLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto"></div>
                <p className="text-gray-600 mt-4">Loading appointments...</p>
              </div>
            ) : appointments && appointments.length > 0 ? (
              <div className="space-y-4">
                {appointments.map((appointment) => (
                  <div
                    key={appointment.id}
                    className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          {getStatusIcon(appointment.status)}
                          <h3 className="text-lg font-semibold text-gray-900">
                            {appointment.visitor_name || 'Anonymous'}
                          </h3>
                          <span className={`emotion-badge ${getStatusColor(appointment.status)}`}>
                            {appointment.status}
                          </span>
                        </div>
                        
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>📅 {formatDateTime(appointment.start_time)}</p>
                          <p>🆔 Session: {appointment.session_id.slice(0, 8)}...</p>
                        </div>
                      </div>
                      
                      <div className="flex flex-col space-y-2">
                        <button
                          onClick={() => router.push(`/chat/${appointment.session_id}`)}
                          className="btn-primary text-sm flex items-center space-x-2"
                        >
                          <MessageCircle className="w-4 h-4" />
                          <span>Join Chat</span>
                        </button>
                        
                        <button
                          onClick={() => router.push(`/therapist/session/${appointment.session_id}`)}
                          className="btn-outline text-sm"
                        >
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-700 mb-2">No appointments yet</h3>
                <p className="text-gray-600">Appointments will appear here when users book them.</p>
              </div>
            )}
          </div>
        )}

        {selectedTab === 'active' && (
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Active Chat Sessions</h2>
            
            {activeLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto"></div>
                <p className="text-gray-600 mt-4">Loading active sessions...</p>
              </div>
            ) : activeSessions && activeSessions.active_sessions.length > 0 ? (
              <div className="space-y-4">
                {activeSessions.active_sessions.map((sessionId: string) => (
                  <div
                    key={sessionId}
                    className="border border-gray-200 rounded-lg p-4 hover:border-green-300 transition-colors bg-green-50"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">Active Session</h3>
                          <p className="text-sm text-gray-600">🆔 {sessionId.slice(0, 8)}...</p>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => router.push(`/chat/${sessionId}`)}
                        className="btn-primary flex items-center space-x-2"
                      >
                        <MessageCircle className="w-5 h-5" />
                        <span>Join Session</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-700 mb-2">No active sessions</h3>
                <p className="text-gray-600">Active chat sessions will appear here.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
