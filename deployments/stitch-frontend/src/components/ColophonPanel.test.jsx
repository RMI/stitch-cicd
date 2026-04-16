import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const makeConfig = (apiBaseUrl) => ({
  appEnv: "local",
  apiBaseUrl,
  build: {
    appVersion: "0.0.0",
    buildId: "local-build",
    gitSha: "abcdef123456",
    nodeVersion: "v20.19.0",
    viteVersion: "^7.2.4",
    buildTime: "2026-04-06T12:00:00Z",
  },
});

vi.mock("../config/env", () => ({
  default: makeConfig("http://localhost:8000/api/v1"),
}));

describe("ColophonPanel", () => {
  let fetchMock;

  beforeEach(() => {
    fetchMock = vi.fn().mockResolvedValue({ ok: true, json: vi.fn() });
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders API docs link when URL is valid", async () => {
    const { default: ColophonPanel } = await import("./ColophonPanel");
    render(<ColophonPanel diagnosticsOpen />);

    const link = screen.getByRole("link", { name: "API docs" });
    expect(link).toHaveAttribute("href", "http://localhost:8000/docs");
  });

  it("renders unavailable state when API docs URL cannot be derived", async () => {
    vi.doMock("../config/env", () => ({
      default: makeConfig("http://localhost:8000"),
    }));

    const { default: ColophonPanel } = await import("./ColophonPanel");
    render(<ColophonPanel diagnosticsOpen />);

    expect(screen.getByText("API docs unavailable")).toBeInTheDocument();
  });
});
