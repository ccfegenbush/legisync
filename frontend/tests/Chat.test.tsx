import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import Chat from "@/components/Chat";

const server = setupServer(
  http.post("/api/rag", () => {
    return HttpResponse.json({
      result: "Mock summary",
      documents_found: 2,
    });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test("submits query and displays response", async () => {
  render(<Chat />);

  const textarea = screen.getByPlaceholderText(
    "Ask about Texas bills... (Press Enter to send)"
  );
  const submitButton = screen.getByRole("button");

  fireEvent.change(textarea, {
    target: { value: "Test query" },
  });
  fireEvent.click(submitButton);

  // Wait for the response to appear
  await waitFor(() => {
    expect(screen.getByText("Mock summary")).toBeInTheDocument();
  });
});
