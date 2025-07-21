"use client";

interface ExampleQuery {
  text: string;
  description: string;
  icon: string;
  category: string;
}

interface ExampleQueriesProps {
  onQueryClick: (query: string) => void;
}

export default function ExampleQueries({ onQueryClick }: ExampleQueriesProps) {
  const examples: ExampleQuery[] = [
    {
      text: "Education funding for public schools",
      description: "Find bills related to school finance and education budgets",
      icon: "🎓",
      category: "education",
    },
    {
      text: "Healthcare legislation for rural areas",
      description: "Discover healthcare initiatives for rural communities",
      icon: "🏥",
      category: "healthcare",
    },
    {
      text: "Property tax relief measures",
      description: "Explore bills aimed at reducing property taxes",
      icon: "💰",
      category: "taxes",
    },
    {
      text: "Environmental protection bills",
      description: "Find legislation focused on environmental conservation",
      icon: "🌱",
      category: "environment",
    },
    {
      text: "Criminal justice reform proposals",
      description: "Discover bills addressing criminal justice system changes",
      icon: "⚖️",
      category: "justice",
    },
    {
      text: "Small business support legislation",
      description: "Find bills supporting small business development",
      icon: "🏢",
      category: "business",
    },
  ];

  return (
    <div className="bg-blue-50 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        ✨ Try these example queries:
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {examples.map((example, idx) => (
          <button
            key={idx}
            onClick={() => onQueryClick(example.text)}
            className="bg-white rounded-lg p-4 text-left border border-blue-200 hover:border-blue-400 hover:shadow-md transition-all duration-200 group"
          >
            <div className="flex items-start space-x-3">
              <div className="text-2xl group-hover:scale-110 transition-transform duration-200">
                {example.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-gray-900 mb-1 group-hover:text-blue-700 transition-colors">
                  &ldquo;{example.text}&rdquo;
                </div>
                <div className="text-xs text-gray-600 line-clamp-2">
                  {example.description}
                </div>
                <div className="mt-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {example.category}
                  </span>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">
          💡 Click any example to instantly search, or type your own query below
        </p>
      </div>
    </div>
  );
}
