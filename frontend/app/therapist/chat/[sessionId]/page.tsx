"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import TherapistChat from "@/components/TherapistChat";

export default function TherapistChatPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center space-x-4">
            <Link
              href={`/therapist/session/${sessionId}`}
              className="text-primary-600 hover:text-primary-700"
            >
              <ArrowLeft className="w-6 h-6" />
            </Link>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Therapist Chat
              </h1>
              <p className="text-sm text-gray-600">Session: {sessionId}</p>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 container mx-auto px-4 py-6">
        <div className="h-full bg-white rounded-lg shadow">
          <TherapistChat sessionId={sessionId} />
        </div>
      </div>
    </div>
  );
}
