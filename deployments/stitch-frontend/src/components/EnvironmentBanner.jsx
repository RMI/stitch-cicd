import config from "../config/env";

function normalizeEnvLabel(value) {
  return (value ?? "").trim();
}

function isProductionEnv(label) {
  const normalized = label.toLowerCase();
  return normalized === "production" || normalized === "prod";
}

function getBannerClasses(label) {
  const normalized = label.toLowerCase();

  if (normalized === "main") {
    return "bg-green-500 text-white";
  }

  if (normalized === "next") {
    return "bg-yellow-400 text-black";
  }

  if (normalized.startsWith("hotfix")) {
    return "bg-orange-500 text-white";
  }

  if (
    normalized === "development" ||
    normalized === "develop" ||
    normalized === "dev"
  ) {
    return "bg-red-500 text-white";
  }

  if (normalized.startsWith("pr-")) {
    return "bg-indigo-500 text-white";
  }

  if (normalized === "local") {
    return "bg-slate-700 text-white";
  }

  return "bg-pink-500 text-white";
}

export default function EnvironmentBanner() {
  const label = normalizeEnvLabel(config.appEnv);

  if (!label || isProductionEnv(label)) {
    return null;
  }

  return (
    <div className={`${getBannerClasses(label)} sticky top-0 z-50 w-full`}>
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-1 text-sm font-medium">
        <span>{label.toUpperCase()} Environment</span>
        <span className="opacity-80">Diagnostics coming soon</span>
      </div>
    </div>
  );
}
