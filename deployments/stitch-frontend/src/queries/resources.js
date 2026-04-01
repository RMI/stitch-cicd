import { getResource, getResources, getResourceDetail } from "./api";

export const DEFAULT_STALE_TIME = 60_000;
export const DEFAULT_PAGE = 1;
export const DEFAULT_PAGE_SIZE = 10;

// Query key factory - hierarchical for easy invalidation
export const resourceKeys = {
  all: (endpoint = "resources") => [endpoint],
  lists: (endpoint = "resources") => [...resourceKeys.all(endpoint), "list"],
  list: (endpoint = "resources", filters) => [
    ...resourceKeys.lists(endpoint),
    filters,
  ],
  details: (endpoint = "resources") => [
    ...resourceKeys.all(endpoint),
    "detail",
  ],
  detail: (endpoint = "resources", id) => [
    ...resourceKeys.details(endpoint),
    id,
  ],
  views: (endpoint = "resources") => [...resourceKeys.all(endpoint), "view"],
  view: (endpoint = "resources", id) => [...resourceKeys.views(endpoint), id],
};

// Query definitions
export const resourceQueries = {
  list: (endpoint = "resources", page = DEFAULT_PAGE, page_size = DEFAULT_PAGE_SIZE, filters = {}) => ({
    queryKey: resourceKeys.list(endpoint, { page, page_size, ...filters }),
    queryFn: (fetcher) => getResources(fetcher, endpoint, { page, page_size, filters }),
    enabled: false,
    staleTime: DEFAULT_STALE_TIME,
  }),

  detail: (endpoint = "resources", id) => ({
    queryKey: resourceKeys.detail(endpoint, id),
    queryFn: (fetcher) => getResourceDetail(id, fetcher, endpoint),
    enabled: false,
  }),

  view: (endpoint = "resources", id) => ({
    queryKey: resourceKeys.view(endpoint, id),
    queryFn: (fetcher) => getResource(id, fetcher, endpoint),
    enabled: false,
  }),
};
