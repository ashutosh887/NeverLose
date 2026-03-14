import { cn } from "@/lib/utils";

interface SpecsTableProps {
  specs: readonly { label: string; value: string }[];
}

export function SpecsTable({ specs }: SpecsTableProps) {
  return (
    <div className="mt-12">
      <h2 className="text-lg font-extrabold text-gray-900 mb-4">Specifications</h2>
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden shadow-sm">
        {specs.map((spec, i) => (
          <div
            key={spec.label}
            className={cn(
              "flex gap-6 px-6 py-3.5 text-sm",
              i % 2 === 0 ? "bg-white" : "bg-gray-50/60"
            )}
          >
            <span className="w-32 flex-shrink-0 text-gray-400 font-medium text-xs uppercase tracking-wide self-center">
              {spec.label}
            </span>
            <span className="text-gray-800 font-medium">{spec.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
