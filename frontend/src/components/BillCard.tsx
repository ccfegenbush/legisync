"use client";
import { useState } from "react";

interface Bill {
  id: string;
  bill_id: string;
  title: string;
  summary?: string;
  session: string;
  status?: string;
  bill_type: string;
  introduced_date?: string;
  authors?: string[];
  subjects?: string[];
}

interface BillCardProps {
  bill: Bill;
  searchTerm?: string;
  isModal?: boolean;
  onClose?: () => void;
}

export default function BillCard({
  bill,
  searchTerm,
  isModal = false,
  onClose,
}: BillCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getBillTypeColor = (type: string) => {
    switch (type.toUpperCase()) {
      case "HB":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "SB":
        return "bg-green-100 text-green-800 border-green-200";
      case "HR":
      case "SR":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "HCR":
      case "SCR":
        return "bg-orange-100 text-orange-800 border-orange-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const highlightText = (text: string, term?: string) => {
    if (!term) return text;
    const regex = new RegExp(`(${term})`, "gi");
    return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
  };

  // Modal wrapper for when isModal is true
  if (isModal) {
    return (
      <div
        className="fixed inset-0 bg-white bg-opacity-75 backdrop-blur-sm flex items-center justify-center p-4 z-[60]"
        onClick={onClose}
      >
        <div
          className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto shadow-2xl border border-gray-200 relative z-[61]"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button for modal */}
          <div className="flex justify-end p-4 pb-0">
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Modal content - same as regular card but without outer container styling */}
          <div className="px-6 pb-6">
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium border ${getBillTypeColor(
                    bill.bill_type
                  )}`}
                >
                  {bill.bill_id}
                </span>
                <span className="text-sm text-gray-600">
                  Session {bill.session}
                </span>
              </div>
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  className={`w-5 h-5 transition-transform duration-200 ${
                    isExpanded ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
            </div>

            {/* Title */}
            <h3
              className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2"
              dangerouslySetInnerHTML={{
                __html: highlightText(bill.title, searchTerm),
              }}
            />

            {/* Summary Preview */}
            {bill.summary && (
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                {bill.summary.length > 150 && !isExpanded
                  ? `${bill.summary.slice(0, 150)}...`
                  : bill.summary}
              </p>
            )}

            {/* Status */}
            {bill.status && (
              <div className="mb-3">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Status: {bill.status}
                </span>
              </div>
            )}

            {/* Expanded Details */}
            {isExpanded && (
              <div className="border-t border-gray-200 pt-4 mt-4 space-y-3">
                {/* Authors */}
                {bill.authors && bill.authors.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">
                      Authors:
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {bill.authors.map((author, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                        >
                          {author}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Subjects */}
                {bill.subjects && bill.subjects.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">
                      Subjects:
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {bill.subjects.map((subject, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                        >
                          {subject}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Date */}
                {bill.introduced_date && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">
                      Introduced:
                    </h4>
                    <span className="text-sm text-gray-600">
                      {new Date(bill.introduced_date).toLocaleDateString()}
                    </span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex space-x-2 pt-3">
                  <button className="px-3 py-1 bg-blue-50 text-blue-700 rounded-md text-sm font-medium hover:bg-blue-100 transition-colors">
                    View Full Text
                  </button>
                  <button className="px-3 py-1 bg-gray-50 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors">
                    View Actions
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-all duration-200 hover:shadow-md">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium border ${getBillTypeColor(
                bill.bill_type
              )}`}
            >
              {bill.bill_id}
            </span>
            <span className="text-sm text-gray-600">
              Session {bill.session}
            </span>
          </div>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg
              className={`w-5 h-5 transition-transform duration-200 ${
                isExpanded ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        </div>

        {/* Title */}
        <h3
          className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2"
          dangerouslySetInnerHTML={{
            __html: highlightText(bill.title, searchTerm),
          }}
        />

        {/* Summary Preview */}
        {bill.summary && (
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">
            {bill.summary.length > 150 && !isExpanded
              ? `${bill.summary.slice(0, 150)}...`
              : bill.summary}
          </p>
        )}

        {/* Status */}
        {bill.status && (
          <div className="mb-3">
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              Status: {bill.status}
            </span>
          </div>
        )}

        {/* Expanded Details */}
        {isExpanded && (
          <div className="border-t border-gray-200 pt-4 mt-4 space-y-3">
            {/* Authors */}
            {bill.authors && bill.authors.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-1">
                  Authors:
                </h4>
                <div className="flex flex-wrap gap-1">
                  {bill.authors.map((author, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      {author}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Subjects */}
            {bill.subjects && bill.subjects.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-1">
                  Subjects:
                </h4>
                <div className="flex flex-wrap gap-1">
                  {bill.subjects.map((subject, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                    >
                      {subject}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Date */}
            {bill.introduced_date && (
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-1">
                  Introduced:
                </h4>
                <span className="text-sm text-gray-600">
                  {new Date(bill.introduced_date).toLocaleDateString()}
                </span>
              </div>
            )}

            {/* Actions */}
            <div className="flex space-x-2 pt-3">
              <button className="px-3 py-1 bg-blue-50 text-blue-700 rounded-md text-sm font-medium hover:bg-blue-100 transition-colors">
                View Full Text
              </button>
              <button className="px-3 py-1 bg-gray-50 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors">
                View Actions
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
