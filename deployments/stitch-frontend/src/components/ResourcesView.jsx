import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useResources } from "../hooks/useResources";
import FetchButton from "./FetchButton";
import ClearCacheButton from "./ClearCacheButton";
import ResourcesTable from "./ResourcesTable";
import FilterBar from "./FilterBar";
import Pagination from "./Pagination";
import { EMPTY_FILTERS } from "../config/filters";
import { resourceKeys, DEFAULT_PAGE_SIZE, DEFAULT_PAGE } from "../queries/resources";
import config from "../config/env";

// OR within a field, AND across fields.
function applyFilters(resources, filters) {
  if (!resources) return resources;
  return resources.filter((resource) =>
    Object.entries(filters).every(
      ([field, values]) => !values.length || values.includes(resource[field]),
    ),
  );
}

export default function ResourcesView({ className, endpoint }) {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [enabled, setEnabled] = useState(false);
  const [filters, setFilters] = useState(EMPTY_FILTERS);

  const { data, isLoading, isError, refetch } = useResources(endpoint, {
    page,
    page_size: pageSize,
    enabled,
  });

  const handleFetch = () => {
    setEnabled(true);
    refetch();
  };

  const handleClear = () => {
    queryClient.removeQueries({ queryKey: resourceKeys.lists(endpoint) });
    setEnabled(false);
    setPage(1);
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (newSize) => {
    setPageSize(newSize);
    setPage(1);
  };

  const filteredData = applyFilters(data?.items, filters);

  return (
    <div className={`max-w-4xl mx-auto ${className}`}>
      <h1 className="text-3xl font-bold mb-3 text-gray-800">Resources</h1>
      <div className="text-gray-500 pb-4">
        <span className="font-bold">
          {config.apiBaseUrl}/{endpoint}
        </span>
      </div>
      <div className="mb-4 flex gap-3">
        <FetchButton onFetch={handleFetch} isLoading={isLoading} />
        <ClearCacheButton
          onClear={handleClear}
          disabled={!data?.items?.length && !isError}
        />
      </div>
      {data?.items?.length > 0 && (
        <div className="mb-4">
          <FilterBar
            resources={data?.items}
            filters={filters}
            onFiltersChange={setFilters}
          />
        </div>
      )}
      {isError && (
        <p className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          Failed to load resources. Check your connection and try again.
        </p>
      )}
      {!isError && data && filteredData?.length === 0 && (
        <p className="text-sm text-gray-400">
          No resources match the current filters.
        </p>
      )}
      <ResourcesTable resources={filteredData} />
      {data && (
        <Pagination
          page={page}
          pageSize={pageSize}
          totalCount={data.total_count}
          totalPages={data.total_pages}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
        />
      )}
    </div>
  );
}
