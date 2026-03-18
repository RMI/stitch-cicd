import { useState } from "react";
import { Link } from "react-router-dom";
import SourceMixBar from "./SourceMixBar";

// sortType: "string" | "number", omit sortable (or set false) to disable sorting for a column.
const COLUMNS = [
  {
    label: "Name",
    key: "name",
    className: "font-medium text-gray-900",
    sortable: true,
    sortType: "string",
  },
  {
    label: "State/Province",
    key: "state_province",
    className: "text-gray-500",
    sortable: true,
    sortType: "string",
  },
  {
    label: "Region",
    key: "region",
    className: "text-gray-500",
    sortable: true,
    sortType: "string",
  },
  {
    label: "Basin",
    key: "basin",
    className: "text-gray-500",
    sortable: true,
    sortType: "string",
  },
];

function getField(resource, key) {
  return resource?.data?.[key] ?? null;
}

// Pure sort utility — accepts the sort config object so it can be
// reused / moved server-side when pagination is introduced.
function applySort(data, sortConfig) {
  if (!sortConfig.column) return data;

  const col = COLUMNS.find((c) => c.key === sortConfig.column);
  if (!col?.sortable) return data;

  return [...data].sort((a, b) => {
    const aVal = getField(a, sortConfig.column);
    const bVal = getField(b, sortConfig.column);

    // Nulls always last, regardless of direction
    if (aVal == null && bVal == null) return 0;
    if (aVal == null) return 1;
    if (bVal == null) return -1;

    const cmp =
      col.sortType === "number"
        ? aVal - bVal
        : String(aVal).localeCompare(String(bVal));

    return sortConfig.direction === "asc" ? cmp : -cmp;
  });
}

function SortIndicator({ column, sortConfig }) {
  if (sortConfig.column !== column) {
    return <span className="ml-1 text-gray-medium">⬍</span>;
  }
  return (
    <span className="ml-1 inline-block scale-y-60 text-gray-dark">
      {sortConfig.direction === "asc" ? "▲" : "▼"}
    </span>
  );
}

export default function ResourcesTable({ resources }) {
  // sortConfig is isolated here for now; lift to parent + pass as prop
  // when server-side sort params are needed for pagination.
  const [sortConfig, setSortConfig] = useState({
    column: null,
    direction: "asc",
  });

  if (!resources?.length) return null;

  function handleSort(key) {
    setSortConfig((prev) => ({
      column: key,
      direction:
        prev.column === key && prev.direction === "asc" ? "desc" : "asc",
    }));
  }

  const sorted = applySort(resources, sortConfig);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-xs font-medium tracking-wide text-gray-500">
            {COLUMNS.map((col) =>
              col.sortable ? (
                <th
                  key={col.key}
                  className="py-2 pr-6"
                  aria-sort={
                    sortConfig.column !== col.key
                      ? "none"
                      : sortConfig.direction === "asc"
                        ? "ascending"
                        : "descending"
                  }
                >
                  <button
                    onClick={() => handleSort(col.key)}
                    className="select-none hover:text-gray-800 cursor-pointer"
                  >
                    {col.label}
                    <SortIndicator column={col.key} sortConfig={sortConfig} />
                  </button>
                </th>
              ) : (
                <th key={col.key} className="py-2 pr-6">
                  {col.label}
                </th>
              ),
            )}
            <th className="py-2 min-w-32">Data source mix</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((resource) => (
            // `relative` on <tr> anchors the Link's ::after pseudo-element,
            // which stretches across the full row for pointer/keyboard/right-click support.
            <tr
              key={resource.id}
              className="relative border-b border-gray-100 transition-colors hover:bg-white"
            >
              {COLUMNS.map((col) => {
                const value = getField(resource, col.key);

                return (
                <td key={col.key} className={`py-2.5 pr-6 ${col.className}`}>
                  {col.key === "name" ? (
                    <Link
                      to={`/oil-gas-fields/${resource.id}`}
                      className="after:absolute after:inset-0 after:content-['']"
                    >
                      {value ?? (
                        <span className="text-gray-300">—</span>
                      )}
                    </Link>
                  ) : (
                    (value ?? (
                      <span className="text-gray-300">—</span>
                    ))
                  )}
                </td>
              )})}

              <td className="py-2.5">
                <SourceMixBar provenance={resource.provenance} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
