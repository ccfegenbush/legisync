import Chat from "@/components/Chat";
import BillFilters from "@/components/BillFilters";

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
          <div className="bg-blue-50 rounded-xl p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Try these example queries:
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="bg-white rounded-lg p-3 text-left border border-blue-200">
                <div className="text-sm font-medium text-gray-900">
                  &ldquo;Education funding for public schools&rdquo;
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  Find bills related to school finance
                </div>
              </div>
              <div className="bg-white rounded-lg p-3 text-left border border-blue-200">
                <div className="text-sm font-medium text-gray-900">
                  &ldquo;Healthcare legislation for rural areas&rdquo;
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  Discover rural healthcare initiatives
                </div>
              </div>
              <div className="bg-white rounded-lg p-3 text-left border border-blue-200">
                <div className="text-sm font-medium text-gray-900">
                  &ldquo;Property tax relief measures&rdquo;
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  Explore tax reduction proposals
                </div>
              </div>
              <div className="bg-white rounded-lg p-3 text-left border border-blue-200">
                <div className="text-sm font-medium text-gray-900">
                  &ldquo;Environmental protection bills&rdquo;
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  Find environmental legislation
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Search Filters */}
        <BillFilters
          onFilterChange={(filters) => console.log("Filters:", filters)}
        />

        {/* Chat Component */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200">
          <Chat />
        </div>

        {/* Feature Cards */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 transition-colors">
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              AI-Powered Search
            </h3>
            <p className="text-gray-600 text-sm">
              Advanced natural language processing understands your queries and
              finds the most relevant bills.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-green-300 transition-colors">
            <div className="text-3xl mb-3">⚡</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Real-Time Data
            </h3>
            <p className="text-gray-600 text-sm">
              Our database is continuously updated with the latest bills from
              the Texas Legislature.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border border-gray-200 hover:border-purple-300 transition-colors">
            <div className="text-3xl mb-3">📊</div>
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
                  Powered by AI • Built with ❤️ for Texas
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6 text-sm text-gray-600">
              <a href="#" className="hover:text-blue-600 transition-colors">
                📖 About
              </a>
              <a href="#" className="hover:text-blue-600 transition-colors">
                🔧 API
              </a>
              <a href="#" className="hover:text-blue-600 transition-colors">
                📞 Contact
              </a>
              <div className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                ✅ System Healthy
              </div>
            </div>
          </div>
        </div>
      </footer>

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
