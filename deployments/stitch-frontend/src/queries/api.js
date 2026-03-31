import config from "../config/env";

export async function getResources(fetcher, endpoint = "resources") {
  const url = `${config.apiBaseUrl}/${endpoint}/`;
  const response = await fetcher(url);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
}

export async function getResource(id, fetcher, endpoint = "resources") {
  const url = `${config.apiBaseUrl}/${endpoint}/${id}`;
  const response = await fetcher(url);
  if (!response.ok) {
    const error = new Error(`HTTP error! status: ${response.status}`);
    error.status = response.status;
    throw error;
  }
  const data = await response.json();
  return data;
}

export async function getResourceDetail(id, fetcher, endpoint = "resources") {
  const url = `${config.apiBaseUrl}/${endpoint}/${id}/detail`;
  const response = await fetcher(url);
  if (!response.ok) {
    const error = new Error(`HTTP error! status: ${response.status}`);
    error.status = response.status;
    throw error;
  }
  const data = await response.json();
  return data;
}
