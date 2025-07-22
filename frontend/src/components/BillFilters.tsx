"use client";
import { useState } from "react";

interface BillFiltersProps {
  onFilterChange: (filters: FilterState) => void;
}

interface FilterState {
  billType: string;
  category: string;
  session: string;
}

export default function BillFilters({ onFilterChange }: BillFiltersProps) {
  const [filters, setFilters] = useState<FilterState>({
    billType: "all",
    category: "all",
    session: "891",
  });

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const categories = [
    { id: "all", name: "All Categories", icon: "🏛️" },
    { id: "education", name: "Education", icon: "🎓" },
    { id: "healthcare", name: "Healthcare", icon: "🏥" },
    { id: "taxes", name: "Taxes", icon: "💰" },
    { id: "environment", name: "Environment", icon: "🌱" },
    { id: "transportation", name: "Transportation", icon: "🚗" },
    { id: "criminal", name: "Criminal Justice", icon: "⚖️" },
    { id: "business", name: "Business", icon: "🏢" },
  ];

  const billTypes = [
    { id: "all", name: "All Bill Types" },
    { id: "HB", name: "House Bills (HB)" },
    { id: "SB", name: "Senate Bills (SB)" },
    { id: "HR", name: "House Resolutions (HR)" },
    { id: "SR", name: "Senate Resolutions (SR)" },
    { id: "HCR", name: "House Concurrent Res." },
    { id: "SCR", name: "Senate Concurrent Res." },
  ];

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Search Filters
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Bill Type Filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">
            Bill Type
          </label>
          <select
            value={filters.billType}
            onChange={(e) => handleFilterChange("billType", e.target.value)}
            className="w-full px-3 py-2 border text-gray-700 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {billTypes.map((type) => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
        </div>

        {/* Category Filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">
            Category
          </label>
          <select
            value={filters.category}
            onChange={(e) => handleFilterChange("category", e.target.value)}
            className="w-full px-3 py-2 border text-gray-700 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.icon} {cat.name}
              </option>
            ))}
          </select>
        </div>

        {/* Session Filter */}
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">
            Legislative Session
          </label>
          <select
            value={filters.session}
            onChange={(e) => handleFilterChange("session", e.target.value)}
            className="w-full px-3 py-2 border text-gray-700 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="891">89th Legislature (2025)</option>
            <option value="all">All Sessions</option>
          </select>
        </div>
      </div>

      {/* Quick Category Buttons */}
      <div className="mt-6">
        <div className="text-sm font-semibold text-gray-900 mb-3">
          Quick Categories:
        </div>
        <div className="flex flex-wrap gap-2">
          {categories.slice(1).map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleFilterChange("category", cat.id)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                filters.category === cat.id
                  ? "bg-blue-100 text-blue-800 border border-blue-300"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {cat.icon} {cat.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
