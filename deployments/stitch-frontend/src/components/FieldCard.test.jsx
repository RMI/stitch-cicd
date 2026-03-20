import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FieldCard, FieldGrid } from "./FieldCard";
import { SOURCE_COLORS, DEFAULT_FIELD_COLOR } from "../constants/sourceMeta";

describe("FieldCard", () => {
  it("renders the label", () => {
    render(<FieldCard label="Country" value="Kuwait" />);
    expect(screen.getByText("Country")).toBeInTheDocument();
  });

  it("renders a string value", () => {
    render(<FieldCard label="Country" value="Kuwait" />);
    expect(screen.getByText("Kuwait")).toBeInTheDocument();
  });

  it("renders a numeric value as a string", () => {
    render(<FieldCard label="Discovery Year" value={1938} />);
    expect(screen.getByText("1938")).toBeInTheDocument();
  });

  it("renders an em dash for null value", () => {
    render(<FieldCard label="Basin" value={null} />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("renders an em dash for undefined value", () => {
    render(<FieldCard label="Basin" value={undefined} />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("renders an em dash for empty string value", () => {
    render(<FieldCard label="Basin" value="" />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("applies the border color for a known source", () => {
    const { container } = render(
      <FieldCard label="Country" value="Kuwait" source="gem" />,
    );
    // The value box is the only element with an inline border-left style
    const valueBox = container.querySelector("[style]");
    expect(valueBox).toHaveStyle({ borderLeftColor: SOURCE_COLORS.gem });
  });

  it("falls back to the default border color for an unknown source", () => {
    const { container } = render(
      <FieldCard label="Country" value="Kuwait" source="unknown" />,
    );
    const valueBox = container.querySelector("[style]");
    expect(valueBox).toHaveStyle({ borderLeftColor: DEFAULT_FIELD_COLOR });
  });

  it("uses the default border color when source is omitted", () => {
    const { container } = render(<FieldCard label="Country" value="Kuwait" />);
    const valueBox = container.querySelector("[style]");
    expect(valueBox).toHaveStyle({ borderLeftColor: DEFAULT_FIELD_COLOR });
  });
});

describe("FieldGrid", () => {
  it("renders its children", () => {
    render(
      <FieldGrid>
        <FieldCard label="Name" value="Burgan" />
        <FieldCard label="Country" value="Kuwait" />
      </FieldGrid>,
    );
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Country")).toBeInTheDocument();
  });
});
