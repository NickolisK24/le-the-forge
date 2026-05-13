import type { V2ApiEnvelope } from "@/lib/v2ApiEnvelope";
import { getV2SourcePath, summarizeObject, summarizeV2Support } from "@/lib/v2ApiEnvelope";

interface V2EnvelopePanelsProps {
  response: V2ApiEnvelope | null;
}

export function V2EnvelopePanels({ response }: V2EnvelopePanelsProps) {
  if (!response) return null;

  return (
    <section className="grid gap-3 lg:grid-cols-3">
      <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <h2 className="text-sm font-semibold text-gray-100">Support summary</h2>
        <p className="mt-2 break-words font-mono text-xs text-gray-300">{summarizeV2Support(response)}</p>
        <p className="mt-2 text-xs text-gray-500">Stable-calculable values remain backend-controlled.</p>
      </div>

      <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <h2 className="text-sm font-semibold text-gray-100">Provenance</h2>
        <p className="mt-2 break-all font-mono text-xs text-gray-300">{getV2SourcePath(response)}</p>
        <p className="mt-2 break-words font-mono text-xs text-gray-500">
          {summarizeObject(response.provenance)}
        </p>
      </div>

      <div className="rounded border border-[#2a3050] bg-[#10152a] p-4">
        <h2 className="text-sm font-semibold text-gray-100">Debug contract</h2>
        <p className="mt-2 break-words font-mono text-xs text-gray-300">
          {summarizeObject(response.meta)}
        </p>
        <p className="mt-2 break-words font-mono text-xs text-gray-500">
          {summarizeObject(response.debug)}
        </p>
      </div>
    </section>
  );
}
