import { type ClassValue, clsx } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function getEmotionColor(emotion?: string): string {
  if (!emotion) return 'bg-gray-200 text-gray-800'
  
  const emotionColors: Record<string, string> = {
    joy: 'bg-yellow-200 text-yellow-900',
    happiness: 'bg-yellow-200 text-yellow-900',
    sadness: 'bg-blue-200 text-blue-900',
    anger: 'bg-red-200 text-red-900',
    fear: 'bg-purple-200 text-purple-900',
    anxiety: 'bg-purple-200 text-purple-900',
    surprise: 'bg-pink-200 text-pink-900',
    disgust: 'bg-green-200 text-green-900',
    neutral: 'bg-gray-200 text-gray-800',
  }
  
  return emotionColors[emotion.toLowerCase()] || 'bg-gray-200 text-gray-800'
}

export function formatDateTime(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

export function formatTime(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
