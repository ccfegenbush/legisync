import { TextEncoder, TextDecoder } from "util";
import "whatwg-fetch";

// Add global polyfills for Node.js environment
Object.assign(global, {
  TextEncoder: TextEncoder,
  TextDecoder: TextDecoder,
  fetch: globalThis.fetch,
  Request: globalThis.Request,
  Response: globalThis.Response,
  Headers: globalThis.Headers,
});

// Mock DOM APIs not available in test environment
Element.prototype.scrollIntoView = jest.fn();

// Import jest-dom matchers - this must come after polyfills
import "@testing-library/jest-dom";

// Mock Next.js router
jest.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    };
  },
  useSearchParams() {
    return new URLSearchParams();
  },
  usePathname() {
    return "";
  },
}));

// Mock fetch globally
global.fetch = jest.fn();

// Increase test timeout for async operations
jest.setTimeout(10000);
