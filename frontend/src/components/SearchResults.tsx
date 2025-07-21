"use client";
import { useState } from "react";
import BillCard from "./BillCard";

interface SearchResult {
  query: string;
  result: string;
  documents_found: number;
  bills?: Array<{
    bill_id: string;
    title: string;
    session: string;
    status?: string;
    bill_type: string;
    summary?: string;
  }>;
}

interface SearchResultsProps {
  searchResult: SearchResult | null;
  isLoading: boolean;
}

export default function SearchResults({
  searchResult,
  isLoading,
}: SearchResultsProps) {
  const [viewMode, setViewMode] = useState<"summary" | "bills">("summary");

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            Searching Texas legislative database...
          </p>
        </div>
      </div>
    );
  }

  if (!searchResult) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <div className="text-center text-gray-500">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            🔍
          </div>
          <h3 className="text-lg font-medium mb-2">Ready to Search</h3>
          <p>Enter a query above to find relevant Texas legislative bills.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Result Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Search Results
            </h3>
            <p className="text-sm text-gray-600">
              Query: &ldquo;{searchResult.query}&rdquo;
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">
              {searchResult.documents_found}
            </div>
            <div className="text-sm text-gray-600">Bills Found</div>
          </div>
        </div>

        {/* View Toggle */}
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode("summary")}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === "summary"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            📝 AI Summary
          </button>
          <button
            onClick={() => setViewMode("bills")}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === "bills"
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            📋 Bill Details
          </button>
        </div>
      </div>

      {/* Content */}
      {viewMode === "summary" ? (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
              {searchResult.result}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex flex-wrap gap-2">
              <button className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium hover:bg-blue-100 transition-colors">
                💾 Export Summary
              </button>
              <button className="px-3 py-1 bg-gray-50 text-gray-700 rounded-full text-sm font-medium hover:bg-gray-100 transition-colors">
                📊 View Analytics
              </button>
              <button
                onClick={() => setViewMode("bills")}
                className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm font-medium hover:bg-green-100 transition-colors"
              >
                📋 View Bill Details
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {searchResult.bills && searchResult.bills.length > 0 ? (
            searchResult.bills.map((bill, idx) => (
              <BillCard
                key={`${bill.bill_id}-${idx}`}
                bill={{
                  id: `${bill.bill_id}-${idx}`,
                  ...bill,
                }}
                searchTerm={searchResult.query}
              />
            ))
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
              <div className="text-gray-500">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  📋
                </div>
                <h3 className="text-lg font-medium mb-2">
                  No Bill Details Available
                </h3>
                <p className="text-sm">
                  Individual bill details are being processed. Please check the
                  AI summary above for bill references.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
