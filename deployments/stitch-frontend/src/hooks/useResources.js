import { useQuery } from "@tanstack/react-query";
import { useAuthenticatedQuery } from "./useAuthenticatedQuery";
import {
  resourceQueries,
  resourceKeys,
  DEFAULT_PAGE_SIZE,
  DEFAULT_PAGE,
} from "../queries/resources";
import mockResources from "../mockData/og_field_resources.json";

const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === "true";

//--------------------------------
// Real Implementations
//--------------------------------
function useResourcesReal(
  endpoint = "resources",
  {
    page = DEFAULT_PAGE,
    page_size = DEFAULT_PAGE_SIZE,
    enabled = false,
    filters = {},
    sort_by,
    sort_order,
  } = {},
) {
  return useAuthenticatedQuery({
    ...resourceQueries.list(
      endpoint,
      page,
      page_size,
      filters,
      sort_by,
      sort_order,
    ),
    enabled,
  });
}

function useResourceReal(endpoint = "resources", id) {
  return useAuthenticatedQuery(resourceQueries.view(endpoint, id));
}

function useResourceDetailReal(endpoint = "resources", id) {
  return useAuthenticatedQuery(resourceQueries.detail(endpoint, id));
}

//--------------------------------
// Mock Implementations
//--------------------------------
function useResourcesMock(
  endpoint = "resources",
  { page = DEFAULT_PAGE, page_size = DEFAULT_PAGE_SIZE } = {},
) {
  return useQuery({
    queryKey: resourceKeys.list(endpoint, { page, page_size }),
    queryFn: () => Promise.resolve(mockResources),
    enabled: false,
  });
}

function useResourceMock(endpoint = "resources", id) {
  return useQuery({
    queryKey: resourceKeys.detail(endpoint, id),
    queryFn: () =>
      Promise.resolve(mockResources.find((r) => r.id === id) ?? null),
    enabled: false,
  });
}

function useResourceDetailMock(endpoint = "resources", id) {
  return useQuery({
    queryKey: resourceKeys.detail(endpoint, id),
    queryFn: () =>
      Promise.resolve(mockResources.find((r) => r.id === id) ?? null),
    enabled: false,
  });
}

// Export one implementation based on the compile-time flag. Assign at module level
export const useResources = USE_MOCK_DATA ? useResourcesMock : useResourcesReal;
export const useResource = USE_MOCK_DATA ? useResourceMock : useResourceReal;
export const useResourceDetail = USE_MOCK_DATA
  ? useResourceDetailMock
  : useResourceDetailReal;
