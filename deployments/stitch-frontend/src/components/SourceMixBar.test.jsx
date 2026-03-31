import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import SourceMixBar from "./SourceMixBar";
import { SOURCE_LABELS } from "../constants/sourceMeta";

const singleSource = { foo: "gem", bar: "gem", baz: null };
const mixedSources = { foo: "gem", bar: "wm", baz: null };
const noSources = { foo: null, bar: null, baz: null };

describe("SourceMixBar", () => {
  it("renders a placeholder bar when all source counts are zero", () => {
    const { container } = render(<SourceMixBar provenance={noSources} />);
    const bar = container.querySelector("[title='No source data']");
    expect(bar).toBeInTheDocument();
  });

  it("renders a placeholder bar when provenance is undefined", () => {
    const { container } = render(<SourceMixBar provenance={undefined} />);
    const bar = container.querySelector("[title='No source data']");
    expect(bar).toBeInTheDocument();
  });

  it("renders bar segments for active sources", () => {
    const { container } = render(<SourceMixBar provenance={mixedSources} />);
    const segments = container.querySelectorAll("[title]");
    // Each active source gets a titled segment
    expect(segments.length).toBeGreaterThanOrEqual(2);
  });

  it("does not render source labels by default", () => {
    render(<SourceMixBar provenance={singleSource} />);
    expect(screen.queryByText(SOURCE_LABELS.gem)).not.toBeInTheDocument();
  });

  it("renders source labels when showLabels is true", () => {
    render(<SourceMixBar provenance={singleSource} showLabels />);
    expect(screen.getByText(SOURCE_LABELS.gem)).toBeInTheDocument();
  });

  it("only renders labels for sources with records", () => {
    render(<SourceMixBar provenance={singleSource} showLabels />);
    // wm has 0 records — its label should not appear
    expect(screen.queryByText(SOURCE_LABELS.wm)).not.toBeInTheDocument();
  });

  it("renders labels for all active sources in a mixed dataset", () => {
    render(<SourceMixBar provenance={mixedSources} showLabels />);
    expect(screen.getByText(SOURCE_LABELS.gem)).toBeInTheDocument();
    expect(screen.getByText(SOURCE_LABELS.wm)).toBeInTheDocument();
  });
});
