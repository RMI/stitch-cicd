const REQUIRED_CONFIG_KEYS = [
  "auth0Domain",
  "auth0ClientId",
  "auth0Audience",
];

const DEFAULT_CONFIG_PATH = "/config.json";

function freezeConfig(runtimeConfig) {
  return Object.freeze({
    auth0: Object.freeze({
      domain: runtimeConfig.auth0Domain,
      clientId: runtimeConfig.auth0ClientId,
      audience: runtimeConfig.auth0Audience,
    }),
    apiBaseUrl: runtimeConfig.apiUrl || "http://localhost:8000/api/v1",
    appEnv: runtimeConfig.appEnv || "development",

    build: Object.freeze({
      appVersion: import.meta.env.VITE_APP_VERSION || "0.0.0-dev",
      buildId: import.meta.env.VITE_BUILD_ID || "local",
      gitSha: import.meta.env.VITE_GIT_SHA || "unknown",
      nodeVersion: import.meta.env.VITE_NODE_VERSION || "unknown",
      viteVersion: import.meta.env.VITE_VITE_VERSION || "unknown",
      buildTime: import.meta.env.VITE_BUILD_TIME || "unknown",
    }),

    entityLinkageBaseUrl:
      runtimeConfig.entityLinkageUrl || "http://localhost:8001/api/v1",
  });
}

function validateRuntimeConfig(config) {
  if (!config || typeof config !== "object") {
    throw new Error("Runtime config is missing or invalid.");
  }

  const missing = REQUIRED_CONFIG_KEYS.filter((key) => !config[key]);

  if (missing.length > 0) {
    throw new Error(
      `Missing required runtime config values: ${missing.join(", ")}. ` +
        `Check ${DEFAULT_CONFIG_PATH} or deployment config.`,
    );
  }

  return config;
}

export async function loadConfig() {
  const response = await fetch(DEFAULT_CONFIG_PATH, {
    cache: "no-store",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(
      `Failed to load runtime config from ${DEFAULT_CONFIG_PATH}: ${response.status} ${response.statusText}`,
    );
  }

  const runtimeConfig = validateRuntimeConfig(await response.json());
  return freezeConfig(runtimeConfig);
}

export default loadConfig;
