import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

const handlers = [
  http.post("/api/rag", async ({ request }) => {
    const body = await request.json();
    const query = body.query;

    // Mock different responses based on query
    if (query.includes("error")) {
      return HttpResponse.json(
        { error: "Internal server error" },
        { status: 500 }
      );
    }

    return HttpResponse.json({
      result:
        "Several bills in session 891 relate to education funding for schools. These include:\n\n* **HB 55:** Concerns funding based on property values, considering optional homestead exemptions.\n* **HB 82:** Addresses the use of average enrollment in the public school finance system.",
      documents_found: 4,
      query: query,
    });
  }),
];

export const server = setupServer(...handlers);
