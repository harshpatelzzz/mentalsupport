import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Visitor {
  id: string
  name?: string
  created_at: string
}

export interface Appointment {
  id: string
  visitor_id: string
  session_id: string
  start_time: string
  end_time?: string
  status: 'scheduled' | 'completed' | 'cancelled'
  visitor_name?: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  sender_type: 'visitor' | 'therapist' | 'ai'
  content: string
  emotion?: string
  confidence?: number
  is_read: string
  created_at: string
}

export interface EmotionTrend {
  timestamp: string
  emotion: string
  confidence: number
  session_id: string
}

export interface AnalyticsSummary {
  total_sessions: number
  total_messages: number
  sessions_per_day: Record<string, number>
  emotion_distribution: Record<string, number>
  average_chat_duration: number
  appointment_completion_rate: number
  recent_emotion_trends: EmotionTrend[]
}

// Chat API
export const chatApi = {
  createSession: async (visitorName?: string) => {
    const response = await api.post('/api/chat/session/create', null, {
      params: { visitor_name: visitorName }
    })
    return response.data
  },

  getChatHistory: async (sessionId: string, limit: number = 100) => {
    const response = await api.get<ChatMessage[]>(`/api/chat/messages/${sessionId}`, {
      params: { limit }
    })
    return response.data
  },

  getSessionStats: async (sessionId: string) => {
    const response = await api.get(`/api/chat/session/${sessionId}/stats`)
    return response.data
  },

  therapistJoinAppointment: async (appointmentId: string) => {
    const response = await api.post(`/api/chat/therapist/join/${appointmentId}`)
    return response.data
  },
}

// Appointments API
export const appointmentsApi = {
  create: async (data: { visitor_name?: string; start_time: string }) => {
    const response = await api.post<Appointment>('/api/appointments/', data)
    return response.data
  },

  getAll: async (status?: string, limit: number = 100) => {
    const response = await api.get<Appointment[]>('/api/appointments/', {
      params: { status, limit }
    })
    return response.data
  },

  getUpcoming: async (limit: number = 50) => {
    const response = await api.get<Appointment[]>('/api/appointments/upcoming', {
      params: { limit }
    })
    return response.data
  },

  getById: async (id: string) => {
    const response = await api.get<Appointment>(`/api/appointments/${id}`)
    return response.data
  },

  update: async (id: string, data: { status?: string; end_time?: string }) => {
    const response = await api.patch<Appointment>(`/api/appointments/${id}`, data)
    return response.data
  },

  getBySession: async (sessionId: string) => {
    const response = await api.get<Appointment>(`/api/appointments/session/${sessionId}`)
    return response.data
  },
}

// Therapist API
export const therapistApi = {
  createNote: async (data: { appointment_id: string; note: string }) => {
    const response = await api.post('/api/therapist/notes', data)
    return response.data
  },

  getAppointmentNotes: async (appointmentId: string) => {
    const response = await api.get(`/api/therapist/notes/appointment/${appointmentId}`)
    return response.data
  },

  getEmotionTimeline: async (sessionId: string) => {
    const response = await api.get<EmotionTrend[]>(`/api/therapist/emotion-timeline/${sessionId}`)
    return response.data
  },

  getActiveSessions: async () => {
    const response = await api.get('/api/therapist/active-sessions')
    return response.data
  },

  getSessionParticipants: async (sessionId: string) => {
    const response = await api.get(`/api/therapist/session/${sessionId}/participants`)
    return response.data
  },
}

// Analytics API
export const analyticsApi = {
  getSummary: async (days: number = 30) => {
    const response = await api.get<AnalyticsSummary>('/api/analytics/summary', {
      params: { days }
    })
    return response.data
  },
}
