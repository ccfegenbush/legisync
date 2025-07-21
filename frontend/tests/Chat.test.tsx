import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import Chat from "@/components/Chat";

const server = setupServer(
  http.post("/api/rag", () => {
    return HttpResponse.json({ result: "Mock summary" });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test("submits query and displays response", async () => {
  render(<Chat />);
  fireEvent.change(screen.getByPlaceholderText("Ask about a bill..."), {
    target: { value: "Test query" },
  });
  fireEvent.click(screen.getByText("Submit"));
  expect(await screen.findByText("Mock summary")).toBeInTheDocument();
});
