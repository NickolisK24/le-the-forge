import { getV2LimitationCopy, normalizeV2LimitationCode, type V2LimitationCode } from "@/lib/v2Limitations";

interface V2LimitationNoticeProps {
  codes?: unknown[];
  mode?: "compact" | "full";
}

export function V2LimitationNotice({ codes, mode = "compact" }: V2LimitationNoticeProps) {
  const normalizedCodes = normalizeCodes(codes);

  return (
    <div className="rounded border border-amber-400/20 bg-amber-500/5 p-3">
      <h3 className="text-xs font-semibold text-amber-100">What this means</h3>
      <ul className="mt-2 space-y-2 text-xs text-amber-100/90">
        {normalizedCodes.map((code) => {
          const copy = getV2LimitationCopy(code);
          return (
            <li key={code}>
              <span className="font-semibold text-amber-100">{copy.label}: </span>
              <span>{mode === "full" ? copy.full : copy.compact}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function normalizeCodes(codes: unknown[] | undefined): V2LimitationCode[] {
  if (!codes?.length) return ["unknown_limitation"];
  const normalized = codes.map(normalizeV2LimitationCode);
  return Array.from(new Set(normalized));
}
