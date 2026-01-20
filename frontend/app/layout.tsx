import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Providers from '@/components/Providers'
import '@/lib/chart' // Register Chart.js components globally

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NeuroSupport - Mental Health Support Platform',
  description: 'Anonymous mental health support with AI-powered chat and professional therapist connections',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
