import { clsx } from "clsx";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={clsx(
        "animate-pulse bg-forge-surface3 rounded-sm",
        className
      )}
    />
  );
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="flex flex-col gap-2">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={clsx(
            "h-3",
            i === lines - 1 && lines > 1 ? "w-3/4" : "w-full"
          )}
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ height = 120 }: { height?: number }) {
  return (
    <div
      className="animate-pulse bg-forge-surface border border-forge-border rounded overflow-hidden"
      style={{ height }}
    >
      <div className="h-8 bg-forge-surface3 border-b border-forge-border" />
      <div className="p-4 flex flex-col gap-3">
        <Skeleton className="h-3 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
      </div>
    </div>
  );
}

/** Full-page loading skeleton for route-level Suspense boundaries. */
export function PageSkeleton() {
  return (
    <div className="space-y-6">
      {/* Page title area */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
      </div>
      {/* Content grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SkeletonCard height={180} />
        <SkeletonCard height={180} />
      </div>
      <SkeletonCard height={240} />
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="animate-pulse">
      {/* Header row */}
      <div
        className="flex gap-2 border-b border-forge-border bg-forge-surface2 px-4 py-2.5 mb-0"
      >
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="flex-1">
            <Skeleton className="h-3 w-2/3" />
          </div>
        ))}
      </div>

      {/* Data rows */}
      {Array.from({ length: rows }).map((_, row) => (
        <div
          key={row}
          className="flex gap-2 border-b border-forge-border/40 px-4 py-3"
        >
          {Array.from({ length: cols }).map((_, col) => (
            <div key={col} className="flex-1">
              <Skeleton className={clsx("h-3", col === 0 ? "w-full" : "w-2/3")} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
