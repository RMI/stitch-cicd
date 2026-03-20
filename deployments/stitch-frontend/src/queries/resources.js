import { getResource, getResources, getResourceDetail } from "./api";

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
  list: (endpoint = "resources") => ({
    queryKey: resourceKeys.lists(endpoint),
    queryFn: (fetcher) => getResources(fetcher, endpoint),
    enabled: false,
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
