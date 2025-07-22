"use client";

import { useEffect, useState, useCallback } from "react";

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

  const fetchBillDetails = useCallback(async (billId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Enhanced mock data based on common Texas legislative patterns
      // In real implementation, this would call OpenStates API or Texas Legislature API
      await new Promise((resolve) => setTimeout(resolve, 500));

      // Extract bill type and number for more realistic data
      const [billType, billNumber] = billId.split(" ");
      const isHouseBill = billType.startsWith("H");

      // Generate more realistic mock data based on bill type and number
      const mockDataMap: Record<string, Partial<BillDetails>> = {
        "HB 55": {
          title: "HB 55: Public School Finance and Property Tax Relief",
          description:
            "A bill relating to public school finance and property tax relief; providing for the reduction of the amount of a limitation on the total amount of ad valorem taxes that may be imposed for public school purposes on the residence homestead of a taxpayer.",
          authors: ["Rep. Greg Bonnen", "Rep. Trent Ashby", "Rep. Ken King"],
          status: "Passed - House",
          committee: "House Committee on Public Education",
          introduced_date: "2025-01-14",
          last_action: "Read third time and passed by the House",
          subjects: [
            "Education",
            "Public School Finance",
            "Property Tax",
            "Homestead Exemptions",
          ],
        },
        "HB 82": {
          title: "HB 82: Public School Finance System Enrollment Calculation",
          description:
            "A bill relating to the use of average enrollment in the public school finance system for purposes of calculating state aid for public schools.",
          authors: ["Rep. Dan Huberty", "Rep. Harold Dutton"],
          status: "In Committee",
          committee: "House Committee on Public Education",
          introduced_date: "2025-01-15",
          last_action: "Referred to House Committee on Public Education",
          subjects: ["Education", "School Finance", "Enrollment", "State Aid"],
        },
        "SB 28": {
          title: "SB 28: Healthcare Access in Rural Communities",
          description:
            "A bill relating to improving healthcare access and services in rural communities through expanded telemedicine services and rural health clinic support.",
          authors: ["Sen. Charles Perry", "Sen. Pete Flores"],
          status: "In Committee",
          committee: "Senate Committee on Health & Human Services",
          introduced_date: "2025-01-12",
          last_action:
            "Referred to Senate Committee on Health & Human Services",
          subjects: [
            "Healthcare",
            "Rural Health",
            "Telemedicine",
            "Healthcare Access",
          ],
        },
      };

      const specificData = mockDataMap[billId] || {};

      const mockDetails: BillDetails = {
        bill_id: billId,
        title: specificData.title || `${billId}: ${getGenericTitle(billType)}`,
        description:
          specificData.description ||
          `This ${billType} addresses important legislative matters affecting Texas residents. The bill follows proper legislative procedures and contains provisions designed to improve various aspects of state governance and public policy.`,
        authors: specificData.authors || [
          isHouseBill ? "Rep. John Smith" : "Sen. Jane Johnson",
          isHouseBill ? "Rep. Maria Garcia" : "Sen. Robert Davis",
        ],
        status:
          specificData.status ||
          (parseInt(billNumber) % 3 === 0
            ? "Passed - House"
            : parseInt(billNumber) % 2 === 0
            ? "In Committee"
            : "Filed"),
        session: "891",
        introduced_date:
          specificData.introduced_date ||
          `2025-01-${10 + (parseInt(billNumber) % 20)}`,
        last_action:
          specificData.last_action ||
          getLastAction(billType, parseInt(billNumber)),
        committee:
          specificData.committee ||
          getCommittee(billType, parseInt(billNumber)),
        subjects: specificData.subjects || getSubjects(parseInt(billNumber)),
        bill_type: billType,
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
  }, []);

  useEffect(() => {
    if (isOpen && bill) {
      fetchBillDetails(bill.bill_id);
    }
  }, [isOpen, bill, fetchBillDetails]);

  // Helper functions for more realistic mock data
  const getGenericTitle = (billType: string): string => {
    const titleMap: Record<string, string> = {
      HB: "House Bill - Legislative Matter",
      SB: "Senate Bill - Legislative Matter",
      HR: "House Resolution",
      SR: "Senate Resolution",
      HCR: "House Concurrent Resolution",
      SCR: "Senate Concurrent Resolution",
    };
    return titleMap[billType] || "Legislative Bill";
  };

  const getLastAction = (billType: string, billNumber: number): string => {
    const actions = [
      `Referred to ${billType.startsWith("H") ? "House" : "Senate"} Committee`,
      "Read first time and referred to committee",
      "Committee report printed and distributed",
      "Read second time and amended",
      "Read third time and passed",
    ];
    return actions[billNumber % actions.length];
  };

  const getCommittee = (billType: string, billNumber: number): string => {
    const houseCommittees = [
      "House Committee on State Affairs",
      "House Committee on Public Education",
      "House Committee on Appropriations",
      "House Committee on Public Health",
      "House Committee on Transportation",
    ];
    const senateCommittees = [
      "Senate Committee on State Affairs",
      "Senate Committee on Education",
      "Senate Committee on Finance",
      "Senate Committee on Health & Human Services",
      "Senate Committee on Transportation",
    ];

    const committees = billType.startsWith("H")
      ? houseCommittees
      : senateCommittees;
    return committees[billNumber % committees.length];
  };

  const getSubjects = (billNumber: number): string[] => {
    const subjectGroups = [
      ["Education", "Public Schools", "Teachers"],
      ["Healthcare", "Public Health", "Medical Services"],
      ["Transportation", "Infrastructure", "Roads"],
      ["Criminal Justice", "Public Safety", "Law Enforcement"],
      ["Environment", "Natural Resources", "Conservation"],
      ["Business", "Economic Development", "Commerce"],
      ["Government Operations", "State Agencies", "Administration"],
    ];
    return subjectGroups[billNumber % subjectGroups.length];
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-white bg-opacity-75 backdrop-blur-sm flex items-center justify-center p-4 z-[60]"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto shadow-2xl border border-gray-200 relative z-[61]"
        onClick={(e) => e.stopPropagation()}
      >
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
