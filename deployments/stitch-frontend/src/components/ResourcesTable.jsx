import { useNavigate } from "react-router-dom";
import SourceMixBar from "./SourceMixBar";

const COLUMNS = [
  { label: "Name", key: "name", className: "font-medium text-gray-900" },
  { label: "State/Province", key: "state_province", className: "text-gray-500" },
  { label: "Region", key: "region", className: "text-gray-500" },
  { label: "Basin", key: "basin", className: "text-gray-500" },
];

export default function ResourcesTable({ resources }) {
  const navigate = useNavigate();

  if (!resources?.length) return null;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 text-left text-xs font-medium tracking-wide text-gray-500">
            {COLUMNS.map((col) => (
              <th key={col.key} className="py-2 pr-6">
                {col.label}
              </th>
            ))}
            <th className="py-2 min-w-32">Data source mix</th>
          </tr>
        </thead>
        <tbody>
          {resources.map((resource) => (
            <tr
              key={resource.id}
              onClick={() => navigate(`/resources/${resource.id}`)}
              className="cursor-pointer border-b border-gray-100 transition-colors hover:bg-white"
            >
              {COLUMNS.map((col) => (
                <td key={col.key} className={`py-2.5 pr-6 ${col.className}`}>
                  {resource[col.key] ?? <span className="text-gray-300">—</span>}
                </td>
              ))}
              <td className="py-2.5">
                <SourceMixBar sourceData={resource.source_data} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
