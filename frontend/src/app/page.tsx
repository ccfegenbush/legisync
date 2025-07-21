import Chat from "@/components/Chat";

export default function Home() {
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
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Instantly find and understand Texas legislative bills using natural
            language. Ask questions about education, healthcare, taxes, and
            more.
          </p>
        </div>

        {/* Chat Component */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200">
          <Chat />
        </div>

        {/* Example Queries */}
        <div className="mt-8 bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Try asking about:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="flex items-center space-x-2 text-gray-700">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>&ldquo;Education funding bills for 2025&rdquo;</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-700">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>&ldquo;Healthcare reform legislation&rdquo;</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-700">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>&ldquo;Tax policy changes&rdquo;</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-700">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span>&ldquo;Environmental protection bills&rdquo;</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white/50">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <p className="text-center text-gray-500 text-sm">
            Built with Next.js, FastAPI, and Pinecone • Deployed on Vercel and
            Render
          </p>
        </div>
      </footer>
    </div>
  );
}
