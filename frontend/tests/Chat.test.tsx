import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
// Import MSW after jest-dom to ensure polyfills are loaded
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import Chat from "@/components/Chat";

const mockApiResponse = {
  result:
    "Several bills in session 891 relate to education funding for schools. These include:\n\n* **HB 55:** Concerns funding based on property values, considering optional homestead exemptions.\n* **HB 82:** Addresses the use of average enrollment in the public school finance system.",
  documents_found: 4,
  query: "education funding for schools",
};

const server = setupServer(
  http.post("/api/rag", () => {
    return HttpResponse.json(mockApiResponse);
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe("Chat Component", () => {
  test("renders chat interface correctly", () => {
    render(<Chat />);

    expect(screen.getByText("AI Assistant")).toBeInTheDocument();
    expect(screen.getByText("Start a conversation")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(
        "Ask about Texas bills... (Press Enter to send)"
      )
    ).toBeInTheDocument();
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  test("submits query and displays response with bill extraction", async () => {
    render(<Chat />);

    const textarea = screen.getByPlaceholderText(
      "Ask about Texas bills... (Press Enter to send)"
    );
    const submitButton = screen.getByRole("button");

    fireEvent.change(textarea, {
      target: { value: "education funding for schools" },
    });
    fireEvent.click(submitButton);

    // Wait for the response to appear
    await waitFor(() => {
      expect(
        screen.getByText(
          /Several bills in session 891 relate to education funding/
        )
      ).toBeInTheDocument();
    });

    // Check if documents found indicator is displayed
    await waitFor(() => {
      expect(
        screen.getByText("Found 4 relevant documents")
      ).toBeInTheDocument();
    });

    // Check if bill references are extracted and displayed
    await waitFor(() => {
      expect(screen.getByText("Referenced Bills:")).toBeInTheDocument();
      expect(screen.getByText("HB 55")).toBeInTheDocument();
      expect(screen.getByText("HB 82")).toBeInTheDocument();
    });
  });

  test("handles initial query prop correctly", async () => {
    render(<Chat initialQuery="test initial query" />);

    const textarea = screen.getByPlaceholderText(
      "Ask about Texas bills... (Press Enter to send)"
    );

    expect(textarea).toHaveValue("test initial query");
  });

  test("calls onQueryChange when query changes", () => {
    const mockOnQueryChange = jest.fn();
    render(<Chat onQueryChange={mockOnQueryChange} />);

    const textarea = screen.getByPlaceholderText(
      "Ask about Texas bills... (Press Enter to send)"
    );

    fireEvent.change(textarea, {
      target: { value: "new query" },
    });

    expect(mockOnQueryChange).toHaveBeenCalledWith("new query");
  });

  test("handles keyboard shortcut (Enter) for submission", async () => {
    render(<Chat />);

    const textarea = screen.getByPlaceholderText(
      "Ask about Texas bills... (Press Enter to send)"
    );

    fireEvent.change(textarea, {
      target: { value: "keyboard test" },
    });

    fireEvent.keyDown(textarea, {
      key: "Enter",
      code: "Enter",
      shiftKey: false,
    });

    await waitFor(() => {
      expect(
        screen.getByText(
          /Several bills in session 891 relate to education funding/
        )
      ).toBeInTheDocument();
    });
  });

  test("shows loading state during API request", async () => {
    render(<Chat />);

    const textarea = screen.getByPlaceholderText(
      "Ask about Texas bills... (Press Enter to send)"
    );
    const submitButton = screen.getByRole("button");

    fireEvent.change(textarea, {
      target: { value: "test query" },
    });
    fireEvent.click(submitButton);

    // Check for loading animation
    expect(document.querySelector(".animate-bounce")).toBeInTheDocument();
  });

  test("clears chat when clear button is clicked", async () => {
    render(<Chat />);

    const textarea = screen.getByPlaceholderText(
      "Ask about Texas bills... (Press Enter to send)"
    );
    const submitButton = screen.getByRole("button");

    // Submit a message first
    fireEvent.change(textarea, {
      target: { value: "test message" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(
          /Several bills in session 891 relate to education funding/
        )
      ).toBeInTheDocument();
    });

    // Now clear the chat
    const clearButton = screen.getByText("Clear Chat");
    fireEvent.click(clearButton);

    // Check that messages are cleared
    expect(
      screen.queryByText(
        /Several bills in session 891 relate to education funding/
      )
    ).not.toBeInTheDocument();
    expect(screen.getByText("Start a conversation")).toBeInTheDocument();
  });

  test("handles API error gracefully", async () => {
    server.use(
      http.post("/api/rag", () => {
        return HttpResponse.json(
          { error: "Internal server error" },
          { status: 500 }
        );
      })
    );

    render(<Chat />);

    const textarea = screen.getByPlaceholderText(
      "Ask about Texas bills... (Press Enter to send)"
    );
    const submitButton = screen.getByRole("button");

    fireEvent.change(textarea, {
      target: { value: "error test" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(
          /Sorry, I encountered an error processing your request/
        )
      ).toBeInTheDocument();
    });
  });
});
