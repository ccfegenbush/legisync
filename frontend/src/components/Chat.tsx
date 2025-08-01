"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import BillDetailsModal from "./BillDetailsModal";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  documentsFound?: number;
  isError?: boolean;
  bills?: BillResult[];
}

interface BillResult {
  bill_id: string;
  title: string;
  session?: string;
  status?: string;
  bill_type?: string;
  score?: number;
}

interface ChatProps {
  initialQuery?: string;
  onQueryChange?: (query: string) => void;
}

export default function Chat({ initialQuery, onQueryChange }: ChatProps = {}) {
  const [query, setQuery] = useState(initialQuery || "");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedBill, setSelectedBill] = useState<BillResult | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Notify parent when query changes
  useEffect(() => {
    if (onQueryChange) {
      onQueryChange(query);
    }
  }, [query, onQueryChange]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = useCallback(
    async (e?: React.FormEvent, customQuery?: string) => {
      e?.preventDefault();
      const queryToUse = customQuery || query;
      if (!queryToUse.trim() || isLoading) return;

      const userMessage: Message = {
        id: Date.now().toString(),
        content: queryToUse.trim(),
        isUser: true,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      if (!customQuery) setQuery(""); // Only clear if not using custom query
      setIsLoading(true);

      try {
        const res = await fetch("/api/rag", {
          method: "POST",
          body: JSON.stringify({ query: userMessage.content }),
          headers: { "Content-Type": "application/json" },
        });

        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }

        const data = await res.json();

        // Extract bill references from the response with a simpler approach
        const billPattern = /(HB|SB|HR|SR|HCR|SCR|HJR|SJR)\s+(\d+)/g;
        const bills: BillResult[] = [];
        let match;

        while ((match = billPattern.exec(data.result)) !== null) {
          const billType = match[1];
          const billNumber = match[2];
          const billId = `${billType} ${billNumber}`;
          bills.push({
            bill_id: billId,
            title: `${billId} - Legislative Bill`, // More descriptive title
            session: "891",
            bill_type: billType,
          });
        }
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.result || "I couldn't process your request.",
          isUser: false,
          timestamp: new Date(),
          documentsFound: data.documents_found,
          isError: data.error || false,
          bills: bills,
        };

        setMessages((prev) => [...prev, botMessage]);
      } catch (err) {
        console.error("Chat error:", err);
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content:
            "Sorry, I encountered an error processing your request. Please try again.",
          isUser: false,
          timestamp: new Date(),
          isError: true,
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [query, isLoading]
  );

  // Update query when initialQuery changes
  useEffect(() => {
    if (initialQuery && initialQuery !== query) {
      setQuery(initialQuery);
      // Auto-submit if there's an initial query and no messages yet
      if (initialQuery.trim() && messages.length === 0) {
        setTimeout(() => handleSubmit(undefined, initialQuery), 100);
      }
    }
  }, [initialQuery, query, messages.length, handleSubmit]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const handleBillClick = (bill: BillResult) => {
    setSelectedBill(bill);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedBill(null);
  };

  return (
    <div className="flex flex-col h-[600px]">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          <span className="font-medium text-gray-900">AI Assistant</span>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="text-gray-500 hover:text-gray-700 text-sm font-medium"
          >
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-8 h-8 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.477 8-10 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.477-8 10-8s10 3.582 10 8z"
                />
              </svg>
            </div>
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm">Ask me about Texas legislative bills!</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.isUser ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.isUser
                    ? "bg-blue-600 text-white"
                    : message.isError
                    ? "bg-red-50 text-red-800 border border-red-200"
                    : "bg-gray-100 text-gray-900"
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>

                {/* Bills Display */}
                {message.bills && message.bills.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <div className="text-sm font-medium text-gray-700 mb-2">
                      Referenced Bills:
                    </div>
                    {message.bills.map((bill, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleBillClick(bill)}
                        className="bg-white rounded-lg p-3 border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                              {bill.bill_type}
                            </span>
                            <span className="font-semibold text-gray-900">
                              {bill.bill_id}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500">
                            Session {bill.session}
                          </div>
                        </div>
                        {bill.title && (
                          <p className="text-sm text-gray-600 mt-1">
                            {bill.title}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {message.documentsFound !== undefined &&
                  message.documentsFound > 0 && (
                    <div className="mt-2 text-xs text-gray-600 bg-gray-200 rounded px-2 py-1 inline-block">
                      Found {message.documentsFound} relevant documents
                    </div>
                  )}
                <div
                  className={`text-xs mt-2 ${
                    message.isUser ? "text-blue-200" : "text-gray-500"
                  }`}
                >
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-3 max-w-[80%]">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-3">
          <div className="flex-1 relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full p-3 pr-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-medium text-gray-900 placeholder-gray-500"
              placeholder="Ask about Texas bills... (Press Enter to send)"
              rows={1}
              disabled={isLoading}
            />
            <div className="absolute right-3 top-3 text-gray-400">
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                />
              </svg>
            </div>
          </div>
          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <svg
                className="w-5 h-5 animate-spin"
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
            ) : (
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </button>
        </form>
      </div>

      {/* Bill Details Modal */}
      <BillDetailsModal
        bill={selectedBill}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
}
