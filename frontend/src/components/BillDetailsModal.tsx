"use client";

import { useEffect, useState } from "react";

interface BillResult {
  bill_id: string;
  title: string;
  session?: string;
  status?: string;
  bill_type?: string;
  score?: number;
}

interface BillDetailsModalProps {
  bill: BillResult | null;
  isOpen: boolean;
  onClose: () => void;
}

interface BillDetails {
  bill_id: string;
  title: string;
  description?: string;
  authors?: string[];
  status: string;
  session: string;
  introduced_date?: string;
  last_action?: string;
  committee?: string;
  subjects?: string[];
  bill_type: string;
  url?: string;
}

export default function BillDetailsModal({
  bill,
  isOpen,
  onClose,
}: BillDetailsModalProps) {
  const [details, setDetails] = useState<BillDetails | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && bill) {
      fetchBillDetails(bill.bill_id);
    }
  }, [isOpen, bill]);

  const fetchBillDetails = async (billId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Mock API call - in real implementation, this would call OpenStates API
      // For now, we'll simulate with mock data based on the bill ID
      await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate network delay

      const mockDetails: BillDetails = {
        bill_id: billId,
        title: `${billId}: Legislative Bill Title`,
        description: `This is a detailed description of ${billId}. This bill addresses important legislative matters and contains provisions that affect various aspects of Texas law. The bill was introduced to address specific concerns and follows proper legislative procedures.`,
        authors: ["Rep. Jane Smith", "Rep. John Doe"],
        status: "In Committee",
        session: "891",
        introduced_date: "2025-01-15",
        last_action: "Referred to Committee on State Affairs",
        committee: "State Affairs",
        subjects: ["Government", "Public Administration", "State Agencies"],
        bill_type: billId.split(" ")[0],
        url: `https://capitol.texas.gov/BillLookup/Text.aspx?LegSess=891&Bill=${billId.replace(
          " ",
          ""
        )}`,
      };

      setDetails(mockDetails);
    } catch (err) {
      setError("Failed to load bill details");
      console.error("Error fetching bill details:", err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Bill Details</h2>
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

        {/* Content */}
        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <svg
                className="w-8 h-8 animate-spin text-blue-600"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span className="ml-2 text-gray-600">
                Loading bill details...
              </span>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <div className="text-red-600 mb-2">{error}</div>
              <button
                onClick={() => bill && fetchBillDetails(bill.bill_id)}
                className="text-blue-600 hover:text-blue-800 text-sm underline"
              >
                Try again
              </button>
            </div>
          ) : details ? (
            <div className="space-y-6">
              {/* Bill Header */}
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {details.bill_type}
                  </span>
                  <span className="text-sm text-gray-500">
                    Session {details.session}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {details.title}
                </h3>
                {details.description && (
                  <p className="text-gray-600 leading-relaxed">
                    {details.description}
                  </p>
                )}
              </div>

              {/* Key Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Status</h4>
                  <p className="text-sm text-gray-600">{details.status}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Committee</h4>
                  <p className="text-sm text-gray-600">{details.committee}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Introduced</h4>
                  <p className="text-sm text-gray-600">
                    {details.introduced_date
                      ? new Date(details.introduced_date).toLocaleDateString()
                      : "N/A"}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">
                    Last Action
                  </h4>
                  <p className="text-sm text-gray-600">{details.last_action}</p>
                </div>
              </div>

              {/* Authors */}
              {details.authors && details.authors.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Authors</h4>
                  <div className="flex flex-wrap gap-2">
                    {details.authors.map((author, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
                      >
                        {author}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Subjects */}
              {details.subjects && details.subjects.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Subjects</h4>
                  <div className="flex flex-wrap gap-2">
                    {details.subjects.map((subject, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                      >
                        {subject}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* External Link */}
              {details.url && (
                <div className="pt-4 border-t border-gray-200">
                  <a
                    href={details.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <span>View Full Text</span>
                    <svg
                      className="w-4 h-4 ml-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                      />
                    </svg>
                  </a>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
