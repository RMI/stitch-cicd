const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

// Always returns exactly 7 slots: [first, leftEllipsis, p1, current, p2, rightEllipsis, last]
// Each slot is { page, visible, ellipsis }
function getSlots(currentPage, totalPages) {
  const slot = (page, visible = true) => ({ page, visible, ellipsis: false });
  const ellipsis = (visible = true) => ({ page: null, visible, ellipsis: true });

  // Near the start: 1 2 3 4 5 … last
  if (currentPage <= 4) {
    return [
      slot(1),
      slot(2, totalPages >= 2),
      slot(3, totalPages >= 3),
      slot(4, totalPages >= 4),
      slot(5, totalPages >= 5),
      ellipsis(totalPages > 6),
      slot(totalPages, totalPages > 5),
    ];
  }

  // Near the end: 1 … last-4 last-3 last-2 last-1 last
  if (currentPage >= totalPages - 3) {
    return [
      slot(1, totalPages > 5),
      ellipsis(totalPages > 6),
      slot(totalPages - 4, totalPages >= 5),
      slot(totalPages - 3),
      slot(totalPages - 2),
      slot(totalPages - 1),
      slot(totalPages),
    ];
  }

  // Middle: 1 … prev current next … last
  return [slot(1), ellipsis(), slot(currentPage - 1), slot(currentPage), slot(currentPage + 1), ellipsis(), slot(totalPages)];
}

const pageButtonBase =
  "w-9 h-9 flex items-center justify-center rounded text-sm font-medium transition-colors";

export default function Pagination({
  page,
  pageSize,
  totalCount,
  totalPages,
  onPageChange,
  onPageSizeChange,
}) {
  const slots = getSlots(page, totalPages);
  const firstItem = (page - 1) * pageSize + 1;
  const lastItem = Math.min(page * pageSize, totalCount);

  return (
    <div className="flex flex-wrap items-center justify-between gap-y-3 mt-4 text-sm text-gray-600">
      <span>
        Showing {firstItem}–{lastItem} of {totalCount}
      </span>

      {totalPages > 1 && (
        <div className="flex items-center gap-1">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1}
            className={`${pageButtonBase} bg-gray-100 hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed`}
            aria-label="Previous page"
          >
            ‹
          </button>

          {slots.map((slot, i) =>
            slot.ellipsis ? (
              <span
                key={`ellipsis-${i}`}
                style={{ visibility: slot.visible ? "visible" : "hidden" }}
                className="w-9 h-9 flex items-center justify-center text-gray-400 select-none"
                aria-hidden="true"
              >
                …
              </span>
            ) : (
              <button
                key={`slot-${i}`}
                onClick={() => slot.visible && onPageChange(slot.page)}
                aria-current={slot.page === page ? "page" : undefined}
                style={{ visibility: slot.visible ? "visible" : "hidden" }}
                tabIndex={slot.visible ? 0 : -1}  // focusable if visible
                className={`${pageButtonBase} ${
                  slot.page === page
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 hover:bg-gray-200 text-gray-700"
                }`}
              >
                {slot.page}
              </button>
            ),
          )}

          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page === totalPages}
            className={`${pageButtonBase} bg-gray-100 hover:bg-gray-200 disabled:opacity-40 disabled:cursor-not-allowed`}
            aria-label="Next page"
          >
            ›
          </button>
        </div>
      )}

      <div className="flex items-center gap-2">
        <label htmlFor="page-size-select" className="text-gray-600">
          Per page:
        </label>
        <select
          id="page-size-select"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {PAGE_SIZE_OPTIONS.map((size) => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
