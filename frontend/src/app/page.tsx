"use client";

import { useState } from "react";
import Chat from "@/components/Chat";
import BillFilters from "@/components/BillFilters";
import ExampleQueries from "@/components/ExampleQueries";

export default function Home() {
  const [selectedQuery, setSelectedQuery] = useState<string>("");

  const handleExampleQuery = (query: string) => {
    setSelectedQuery(query);
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-blue-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">LegiSync</h1>
              <p className="text-sm text-gray-600">
                AI-powered Texas Legislative Search
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">
            Search Texas Bills with AI
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-6">
            Instantly find and understand Texas legislative bills using natural
            language. Ask questions about education, healthcare, taxes, and
            more.
          </p>

          {/* Statistics */}
          <div className="flex justify-center space-x-8 mb-8">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">11,651</div>
              <div className="text-sm text-gray-600">Bills Indexed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">891</div>
              <div className="text-sm text-gray-600">Current Session</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                AI-Powered
              </div>
              <div className="text-sm text-gray-600">Semantic Search</div>
            </div>
          </div>

          {/* Example Queries */}
          <ExampleQueries onQueryClick={handleExampleQuery} />
        </div>

        {/* Search Filters */}
        <BillFilters
          onFilterChange={(filters) => console.log("Filters:", filters)}
        />

        {/* Chat Component */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200">
          <Chat
            initialQuery={selectedQuery}
            onQueryChange={(query) => {
              // Reset selectedQuery after it's been used to prevent auto-resubmission
              if (query !== selectedQuery) {
                setSelectedQuery("");
              }
            }}
          />
        </div>

        {/* Feature Cards */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 transition-colors">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              AI-Powered Search
            </h3>
            <p className="text-gray-600 text-sm">
              Advanced natural language processing understands your queries and
              finds the most relevant bills.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-green-300 transition-colors">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-3">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Real-Time Data
            </h3>
            <p className="text-gray-600 text-sm">
              Our database is continuously updated with the latest bills from
              the Texas Legislature.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-purple-300 transition-colors">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
              <svg
                className="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Comprehensive Analysis
            </h3>
            <p className="text-gray-600 text-sm">
              Get summaries, bill details, authorship information, and status
              updates all in one place.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-4xl mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <div>
                <div className="font-semibold text-gray-900">LegiSync</div>
                <div className="text-sm text-gray-600">
                  AI-Powered Texas Legislative Search
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <a href="#" className="hover:text-blue-600 transition-colors">
                About
              </a>
              <a href="#" className="hover:text-blue-600 transition-colors">
                API
              </a>
              <a href="#" className="hover:text-blue-600 transition-colors">
                Contact
              </a>
              <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                System Healthy
              </div>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-center text-gray-500 text-sm">
              Built with Next.js, FastAPI, and Pinecone • Deployed on Vercel and
              Render
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
