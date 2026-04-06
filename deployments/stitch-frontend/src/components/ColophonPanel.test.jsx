import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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
  let clipboardWriteText;

  beforeEach(() => {
    fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        status: "ok",
        service: "stitch-api",
        runtime: {
          environment: "dev",
          started_at: "2026-04-06T10:00:00Z",
          uptime_seconds: 123.456,
        },
        auth: {
          disabled: false,
          startup_validated: true,
        },
        frontend: {
          origin: "http://localhost:3000",
        },
        database: {
          dialect: "postgresql",
          host: "localhost",
          port: 5432,
          database: "stitch",
          reachable: true,
        },
        build: {
          app_version: "0.1.0",
          build_id: "api-local",
          git_sha: "1234567890abcdef",
          build_time: "2026-04-06T09:59:00Z",
        },
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    clipboardWriteText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: clipboardWriteText,
      },
    });

    Object.defineProperty(navigator, "language", {
      configurable: true,
      value: "en-US",
    });

    Object.defineProperty(navigator, "userAgent", {
      configurable: true,
      value: "VitestBrowser/1.0",
    });

    Object.defineProperty(navigator, "connection", {
      configurable: true,
      value: {
        effectiveType: "4g",
        downlink: 10,
      },
    });

    Object.defineProperty(window, "innerWidth", {
      configurable: true,
      value: 1440,
    });

    Object.defineProperty(window, "innerHeight", {
      configurable: true,
      value: 900,
    });

    Object.defineProperty(window, "devicePixelRatio", {
      configurable: true,
      value: 2,
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders frontend, backend, and runtime diagnostics", async () => {
    const { default: ColophonPanel } = await import("./ColophonPanel");

    render(<ColophonPanel diagnosticsOpen />);

    expect(screen.getByText("Frontend Build Info")).toBeInTheDocument();
    expect(screen.getByText("Backend Diagnostics")).toBeInTheDocument();
    expect(screen.getByText("Runtime Info")).toBeInTheDocument();

    expect(screen.getByText("http://localhost:8000/api/v1")).toBeInTheDocument();
    expect(screen.getByText("local-build")).toBeInTheDocument();
    expect(screen.getByText("abcdef1")).toBeInTheDocument();
    expect(screen.getByText("v20.19.0")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("stitch-api")).toBeInTheDocument();
    });

    expect(screen.getByText("postgresql")).toBeInTheDocument();
    expect(screen.getByText("true")).toBeInTheDocument();
    expect(screen.getByText("VitestBrowser/1.0")).toBeInTheDocument();
    expect(screen.getByText("1440x900")).toBeInTheDocument();
    expect(screen.getByText("2x")).toBeInTheDocument();
    expect(screen.getByText("4g (10 Mbps)")).toBeInTheDocument();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/health/details",
      {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      },
    );
  });

  it("copies the diagnostics payload", async () => {
    const user = userEvent.setup();
    const { default: ColophonPanel } = await import("./ColophonPanel");

    render(<ColophonPanel diagnosticsOpen />);

    await waitFor(() => {
      expect(screen.getByText("stitch-api")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Copy" }));

    await waitFor(() => {
      expect(clipboardWriteText).toHaveBeenCalledTimes(1);
    });

    const copiedText = clipboardWriteText.mock.calls[0][0];

    expect(copiedText).toContain("### Frontend Build Info ###");
    expect(copiedText).toContain("API Base URL: http://localhost:8000/api/v1");
    expect(copiedText).toContain("App Version: 0.0.0");
    expect(copiedText).toContain("Git SHA: abcdef1");
    expect(copiedText).toContain("### Backend Diagnostics ###");
    expect(copiedText).toContain("Service: stitch-api");
    expect(copiedText).toContain("DB Reachable: true");
    expect(copiedText).toContain("### Runtime Info ###");
    expect(copiedText).toContain("User Agent: VitestBrowser/1.0");
  });
});
