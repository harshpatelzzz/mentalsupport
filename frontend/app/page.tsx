'use client'

import { MessageCircle, Calendar, Heart, Shield, Clock, Users } from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Heart className="w-8 h-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-primary-900">NeuroSupport</h1>
          </div>
          <Link 
            href="/therapist"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Therapist Portal
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
          You're Not Alone
        </h2>
        <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
          Anonymous, compassionate mental health support available 24/7. 
          Start chatting now or book a session with a professional therapist.
        </p>

        {/* Main Action Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-20">
          {/* Chat Now Card */}
          <Link href="/chat/start">
            <div className="card group cursor-pointer transform hover:scale-105 transition-all duration-200 bg-gradient-to-br from-primary-500 to-primary-600 text-white">
              <MessageCircle className="w-16 h-16 mb-4 mx-auto group-hover:scale-110 transition-transform" />
              <h3 className="text-2xl font-bold mb-3">Chat Now</h3>
              <p className="text-primary-50 mb-4">
                Start an anonymous conversation with our AI support assistant. 
                Get immediate help and emotional support.
              </p>
              <div className="inline-flex items-center text-white font-semibold">
                Start Chatting
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>

          {/* Book Appointment Card */}
          <Link href="/appointment/book">
            <div className="card group cursor-pointer transform hover:scale-105 transition-all duration-200 bg-gradient-to-br from-secondary-500 to-secondary-600 text-white">
              <Calendar className="w-16 h-16 mb-4 mx-auto group-hover:scale-110 transition-transform" />
              <h3 className="text-2xl font-bold mb-3">Book Appointment</h3>
              <p className="text-secondary-50 mb-4">
                Schedule a session with a professional therapist. 
                Private, secure, and completely anonymous.
              </p>
              <div className="inline-flex items-center text-white font-semibold">
                Schedule Now
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <Shield className="w-8 h-8 text-primary-600" />
            </div>
            <h4 className="text-lg font-semibold mb-2">100% Anonymous</h4>
            <p className="text-gray-600">
              No login required. Your privacy is our top priority.
            </p>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-secondary-100 rounded-full mb-4">
              <Clock className="w-8 h-8 text-secondary-600" />
            </div>
            <h4 className="text-lg font-semibold mb-2">24/7 Available</h4>
            <p className="text-gray-600">
              Support whenever you need it, day or night.
            </p>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <Users className="w-8 h-8 text-primary-600" />
            </div>
            <h4 className="text-lg font-semibold mb-2">Professional Care</h4>
            <p className="text-gray-600">
              Connect with trained therapists who care about you.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-center text-gray-600 border-t border-gray-200">
        <p className="mb-2">
          If you're in crisis, please contact emergency services or call a crisis hotline immediately.
        </p>
        <p className="text-sm">
          NeuroSupport provides support but is not a substitute for professional medical advice.
        </p>
      </footer>
    </div>
  )
}
