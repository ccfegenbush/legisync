import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import BillFilters from "@/components/BillFilters";

describe("BillFilters Component", () => {
  const mockOnFilterChange = jest.fn();

  beforeEach(() => {
    mockOnFilterChange.mockClear();
  });

  test("renders all filter options correctly", () => {
    render(<BillFilters onFilterChange={mockOnFilterChange} />);

    expect(screen.getByText("🔍 Search Filters")).toBeInTheDocument();
    expect(screen.getByText("Bill Type")).toBeInTheDocument();
    expect(screen.getByText("Category")).toBeInTheDocument();
    expect(screen.getByText("Legislative Session")).toBeInTheDocument();
  });

  test("renders quick category buttons", () => {
    render(<BillFilters onFilterChange={mockOnFilterChange} />);

    expect(screen.getByText("Quick Categories:")).toBeInTheDocument();

    // Use getByRole to specifically target buttons
    expect(
      screen.getByRole("button", { name: "🎓 Education" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "🏥 Healthcare" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "💰 Taxes" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "🌱 Environment" })
    ).toBeInTheDocument();
  });

  test("calls onFilterChange when bill type is changed", () => {
    render(<BillFilters onFilterChange={mockOnFilterChange} />);

    const billTypeSelect = screen.getByDisplayValue("All Bill Types");
    fireEvent.change(billTypeSelect, { target: { value: "HB" } });

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      billType: "HB",
      category: "all",
      session: "891",
    });
  });

  test("calls onFilterChange when category is changed via dropdown", () => {
    render(<BillFilters onFilterChange={mockOnFilterChange} />);

    const categorySelect = screen.getByDisplayValue("🏛️ All Categories");
    fireEvent.change(categorySelect, { target: { value: "education" } });

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      billType: "all",
      category: "education",
      session: "891",
    });
  });

  test("calls onFilterChange when quick category button is clicked", () => {
    render(<BillFilters onFilterChange={mockOnFilterChange} />);

    const educationButton = screen.getByRole("button", {
      name: "🎓 Education",
    });
    fireEvent.click(educationButton);

    expect(mockOnFilterChange).toHaveBeenCalledWith({
      billType: "all",
      category: "education",
      session: "891",
    });
  });

  test("highlights active quick category button", () => {
    render(<BillFilters onFilterChange={mockOnFilterChange} />);

    const educationButton = screen.getByRole("button", {
      name: "🎓 Education",
    });
    fireEvent.click(educationButton);

    expect(educationButton).toHaveClass("bg-blue-100", "text-blue-800");
  });

  test("shows all bill type options", () => {
    render(<BillFilters onFilterChange={mockOnFilterChange} />);

    const billTypeSelect = screen.getByDisplayValue("All Bill Types");

    expect(screen.getByText("All Bill Types")).toBeInTheDocument();
    expect(screen.getByText("House Bills (HB)")).toBeInTheDocument();
    expect(screen.getByText("Senate Bills (SB)")).toBeInTheDocument();
    expect(screen.getByText("House Resolutions (HR)")).toBeInTheDocument();
    expect(screen.getByText("Senate Resolutions (SR)")).toBeInTheDocument();
  });

  test("shows current legislative session as default", () => {
    render(<BillFilters onFilterChange={mockOnFilterChange} />);

    const sessionSelect = screen.getByDisplayValue("89th Legislature (2025)");
    expect(sessionSelect).toBeInTheDocument();
  });
});
