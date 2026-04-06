import { useEffect, useMemo, useState } from "react";
import config from "../config/env";

function getConnectionInfo() {
  const nav = navigator;

  if (!("connection" in nav)) {
    return "Not available";
  }

  const connection = nav.connection;
  const effectiveType = connection?.effectiveType ?? "unknown";
  const downlink = connection?.downlink;

  if (typeof downlink === "number") {
    return `${effectiveType} (${downlink} Mbps)`;
  }

  return effectiveType;
}

function useSystemInfo() {
  const [systemInfo, setSystemInfo] = useState({
    userAgent: "Loading...",
    screenResolution: "Loading...",
    connectionType: "Loading...",
    language: "Loading...",
    devicePixelRatio: "Loading...",
  });

  useEffect(() => {
    setSystemInfo({
      userAgent: navigator.userAgent,
      screenResolution: `${window.innerWidth}x${window.innerHeight}`,
      connectionType: getConnectionInfo(),
      language: navigator.language || "N/A",
      devicePixelRatio: `${window.devicePixelRatio}x`,
    });
  }, []);

  return systemInfo;
}

function getEnvValue(key, fallback = "N/A") {
  const value = import.meta.env[key];

  if (typeof value === "boolean") {
    return String(value);
  }

  return value?.toString() ?? fallback;
}

export default function ColophonPanel() {
  const systemInfo = useSystemInfo();
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);

  const sections = useMemo(() => {
    return {
      "Build Info": {
        Environment: config.appEnv,
        "API Base URL": config.apiBaseUrl,
        "App Version": getEnvValue("VITE_APP_VERSION"),
        "Build ID": getEnvValue("VITE_BUILD_ID"),
        "Git SHA": getEnvValue("VITE_GIT_SHA").slice(0, 7),
        "Node Version": getEnvValue("VITE_NODE_VERSION"),
        "Vite Version": getEnvValue("VITE_VERSION"),
      },
      "Runtime Info": {
        "User Agent": systemInfo.userAgent,
        "Screen Resolution": systemInfo.screenResolution,
        "Device Pixel Ratio": systemInfo.devicePixelRatio,
        Language: systemInfo.language,
        Connection: systemInfo.connectionType,
      },
    };
  }, [systemInfo]);

  async function handleCopy() {
    const text = Object.entries(sections)
      .map(([section, values]) => {
        const body = Object.entries(values)
          .map(([key, value]) => `${key}: ${value}`)
          .join("\n");

        return `### ${section} ###\n${body}`;
      })
      .join("\n\n");

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setCopyError(false);
      window.setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy diagnostics:", error);
      setCopyError(true);
      setCopied(false);
      window.setTimeout(() => setCopyError(false), 2000);
    }
  }

  return (
    <div className="border-b border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-4xl px-4 py-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <h2 className="text-sm font-semibold text-slate-900">
            Frontend Diagnostics
          </h2>

          <button
            type="button"
            onClick={() => void handleCopy()}
            className="rounded border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-100"
            title="Copy diagnostic information"
          >
            {copied ? "Copied!" : copyError ? "Copy failed" : "Copy"}
          </button>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {Object.entries(sections).map(([section, values]) => (
            <div
              key={section}
              className="rounded border border-slate-200 bg-white p-4"
            >
              <h3 className="mb-2 text-sm font-semibold text-slate-900">
                {section}
              </h3>

              <dl className="space-y-2 text-sm">
                {Object.entries(values).map(([key, value]) => (
                  <div key={key} className="grid grid-cols-[140px_1fr] gap-3">
                    <dt className="font-medium text-slate-700">{key}</dt>
                    <dd className="break-all text-slate-900">{value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
