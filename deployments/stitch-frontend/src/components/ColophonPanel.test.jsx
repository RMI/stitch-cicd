import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const mockConfig = vi.hoisted(() => ({
  appEnv: "local",
  apiBaseUrl: "http://localhost:8000/api/v1",
  build: {
    appVersion: "0.0.0",
    buildId: "local-build",
    gitSha: "abcdef123456",
    nodeVersion: "v20.19.0",
    viteVersion: "^7.2.4",
    buildTime: "2026-04-06T12:00:00Z",
  },
}));

vi.mock("../config/env", () => ({
  default: mockConfig,
}));

describe("ColophonPanel", () => {
  let fetchMock;
  let clipboardSpy;

  beforeEach(() => {
    fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({ status: "ok" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    if (!navigator.clipboard) {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: { writeText: vi.fn() },
      });
    }

    clipboardSpy = vi
      .spyOn(navigator.clipboard, "writeText")
      .mockResolvedValue(undefined);
  });

  afterEach(() => {
    clipboardSpy?.mockRestore();
    vi.unstubAllGlobals();
  });

  it("renders API docs link with correct URL", async () => {
    const { default: ColophonPanel } = await import("./ColophonPanel");

    render(<ColophonPanel diagnosticsOpen />);

    const link = screen.getByRole("link", { name: "API docs" });

    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute(
      "href",
      "http://localhost:8000/docs"
    );
  });
});
