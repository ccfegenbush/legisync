describe("LegiSync Chat", () => {
  beforeEach(() => {
    // Visit the home page before each test
    cy.visit("/");
  });

  it("should display the main components", () => {
    // Check that the main title is visible
    cy.contains("LegiSync").should("be.visible");

    // Check that the input field exists
    cy.get('input[placeholder="Ask about a bill..."]').should("be.visible");

    // Check that the submit button exists
    cy.get("button").contains("Submit").should("be.visible");
  });

  it("should submit query and show response", () => {
    // Intercept the API call to avoid making real backend requests during e2e tests
    cy.intercept("POST", "/api/rag", {
      statusCode: 200,
      body: {
        result:
          "This is a test response about HB1: The General Appropriations Bill",
      },
    }).as("ragQuery");

    // Type in the input field
    cy.get('input[placeholder="Ask about a bill..."]').type("Summarize HB1");

    // Click the submit button
    cy.get("button").contains("Submit").click();

    // Wait for the API call to complete
    cy.wait("@ragQuery");

    // Verify the response is displayed
    cy.contains("This is a test response about HB1").should("be.visible");

    // Verify the input was sent correctly in the API call
    cy.get("@ragQuery").its("request.body").should("deep.equal", {
      query: "Summarize HB1",
    });
  });

  it("should handle empty input gracefully", () => {
    // Try to submit without entering any text
    cy.get("button").contains("Submit").click();

    // The request should still be made, but with empty query
    // You might want to add validation to prevent this in your actual app
  });

  it("should allow multiple queries", () => {
    // Intercept multiple API calls
    cy.intercept("POST", "/api/rag", {
      statusCode: 200,
      body: { result: "First response" },
    }).as("firstQuery");

    // First query
    cy.get('input[placeholder="Ask about a bill..."]').type("First query");
    cy.get("button").contains("Submit").click();
    cy.wait("@firstQuery");
    cy.contains("First response").should("be.visible");

    // Second query - intercept with different response
    cy.intercept("POST", "/api/rag", {
      statusCode: 200,
      body: { result: "Second response" },
    }).as("secondQuery");

    // Clear the input and type new query
    cy.get('input[placeholder="Ask about a bill..."]')
      .clear()
      .type("Second query");
    cy.get("button").contains("Submit").click();
    cy.wait("@secondQuery");
    cy.contains("Second response").should("be.visible");
  });

  // Optional: Test with real backend (remove the intercept)
  it.skip("should work with real backend", () => {
    // This test will make actual API calls to your backend
    // Only run this when you want to test the full integration
    cy.get('input[placeholder="Ask about a bill..."]').type(
      "General Appropriations Bill"
    );
    cy.get("button").contains("Submit").click();

    // Wait for real response (might take longer)
    cy.contains("General Appropriations Bill", { timeout: 10000 }).should(
      "be.visible"
    );
  });
});
