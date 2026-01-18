'use client'

import { useQuery } from '@tanstack/react-query'
import { analyticsApi } from '@/services/api'
import Link from 'next/link'
import { ArrowLeft, TrendingUp, MessageSquare, Calendar, Clock } from 'lucide-react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

export default function AnalyticsPage() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => analyticsApi.getSummary(30),
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">No data available</p>
      </div>
    )
  }

  // Prepare emotion distribution chart data
  const emotionLabels = Object.keys(analytics.emotion_distribution)
  const emotionValues = Object.values(analytics.emotion_distribution)
  
  const emotionChartData = {
    labels: emotionLabels,
    datasets: [
      {
        label: 'Emotion Count',
        data: emotionValues,
        backgroundColor: [
          'rgba(255, 206, 86, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 99, 132, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(201, 203, 207, 0.8)',
        ],
      },
    ],
  }

  // Prepare sessions per day chart data
  const dayLabels = Object.keys(analytics.sessions_per_day).sort()
  const dayValues = dayLabels.map(day => analytics.sessions_per_day[day])
  
  const sessionsChartData = {
    labels: dayLabels.map(d => new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
    datasets: [
      {
        label: 'Sessions',
        data: dayValues,
        borderColor: 'rgb(14, 165, 233)',
        backgroundColor: 'rgba(14, 165, 233, 0.5)',
        tension: 0.3,
      },
    ],
  }

  // Prepare emotion trends chart
  const recentEmotions = analytics.recent_emotion_trends.slice(-20)
  const emotionTrendData = {
    labels: recentEmotions.map(e => new Date(e.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })),
    datasets: [
      {
        label: 'Emotion Confidence',
        data: recentEmotions.map(e => e.confidence),
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.5)',
        tension: 0.3,
      },
    ],
  }

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
                <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
                <p className="text-gray-600 mt-1">Last 30 days performance</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-600">Total Sessions</p>
              <MessageSquare className="w-5 h-5 text-primary-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{analytics.total_sessions}</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-600">Total Messages</p>
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{analytics.total_messages}</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-600">Avg Duration</p>
              <Clock className="w-5 h-5 text-secondary-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{analytics.average_chat_duration.toFixed(1)}</p>
            <p className="text-xs text-gray-500 mt-1">minutes</p>
          </div>

          <div className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-gray-600">Completion Rate</p>
              <Calendar className="w-5 h-5 text-yellow-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{analytics.appointment_completion_rate.toFixed(0)}%</p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Sessions Per Day */}
          <div className="card">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Sessions Per Day</h3>
            <div className="h-64">
              <Line
                data={sessionsChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false,
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        stepSize: 1,
                      },
                    },
                  },
                }}
              />
            </div>
          </div>

          {/* Emotion Distribution */}
          <div className="card">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Emotion Distribution</h3>
            <div className="h-64">
              {emotionLabels.length > 0 ? (
                <Doughnut
                  data={emotionChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom',
                      },
                    },
                  }}
                />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  No emotion data available
                </div>
              )}
            </div>
          </div>

          {/* Emotion Confidence Trend */}
          <div className="card md:col-span-2">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Emotion Analysis Confidence</h3>
            <div className="h-64">
              {recentEmotions.length > 0 ? (
                <Line
                  data={emotionTrendData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
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
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  No emotion trends available
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Emotion Table */}
        {emotionLabels.length > 0 && (
          <div className="card mt-8">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Emotion Breakdown</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Emotion
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Count
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Percentage
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {emotionLabels.map((emotion, index) => {
                    const count = emotionValues[index]
                    const total = emotionValues.reduce((a, b) => a + b, 0)
                    const percentage = ((count / total) * 100).toFixed(1)
                    
                    return (
                      <tr key={emotion}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">
                          {emotion}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {count}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {percentage}%
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
