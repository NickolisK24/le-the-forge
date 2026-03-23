/**
 * Shared UI components.
 * These are the building blocks used across all feature pages.
 * All styled with Tailwind utility classes using the forge theme.
 */

import { clsx } from "clsx";
import type { ReactNode, ButtonHTMLAttributes } from "react";
import type { RiskLevel } from "@/lib/crafting";

// ---------------------------------------------------------------------------
// Panel
// ---------------------------------------------------------------------------

interface PanelProps {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function Panel({ title, action, children, className }: PanelProps) {
  return (
    <div
      className={clsx(
        "rounded border border-forge-border bg-forge-surface overflow-hidden flex flex-col min-w-0",
        className
      )}
    >
      {title && (
        <div className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-4 py-3 shrink-0">
          <span className="font-mono text-xs uppercase tracking-widest text-forge-cyan">
            {title}
          </span>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-4 flex flex-col flex-1 overflow-hidden">{children}</div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Button
// ---------------------------------------------------------------------------

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost" | "danger" | "outline";
  size?: "sm" | "md";
  children: ReactNode;
}

const BUTTON_VARIANTS = {
  primary:
    "bg-forge-amber text-forge-bg hover:bg-forge-amber-hot border-transparent hover:shadow-glow-amber",
  ghost:
    "bg-transparent text-forge-cyan border-forge-cyan/40 hover:text-forge-cyan-hot hover:border-forge-cyan hover:shadow-glow-cyan",
  danger:
    "bg-transparent text-forge-red border border-forge-red/40 hover:bg-forge-red/10 hover:border-forge-red",
  outline:
    "bg-transparent text-forge-muted border-forge-border hover:border-forge-amber hover:text-forge-amber",
};

const BUTTON_SIZES = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-6 py-2.5 text-sm",
};

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={clsx(
        "font-display font-bold tracking-widest uppercase rounded-sm border transition-all duration-150",
        "disabled:opacity-40 disabled:cursor-not-allowed",
        "active:scale-[0.98]",
        BUTTON_VARIANTS[variant],
        BUTTON_SIZES[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Badge
// ---------------------------------------------------------------------------

type BadgeVariant =
  | "ssf" | "hc" | "ladder" | "budget"
  | "tier-s" | "tier-a" | "tier-b" | "tier-c"
  | "patch" | "class" | "mastery" | "default";

const BADGE_STYLES: Record<BadgeVariant, string> = {
  ssf:     "text-forge-amber   border-forge-amber/40   bg-forge-amber/8",
  hc:      "text-forge-red     border-forge-red/40     bg-forge-red/8",
  ladder:  "text-forge-green   border-forge-green/40   bg-forge-green/12",
  budget:  "text-forge-cyan    border-forge-cyan/40    bg-forge-cyan/8",
  "tier-s":"text-forge-gold    border-forge-gold/40    bg-forge-gold/10",
  "tier-a":"text-forge-amber   border-forge-amber/40   bg-forge-amber/8",
  "tier-b":"text-forge-green   border-forge-green/40   bg-forge-green/12",
  "tier-c":"text-forge-muted   border-forge-border",
  patch:   "text-forge-dim     border-forge-border",
  class:   "text-forge-purple  border-forge-purple/40  bg-forge-purple/8",
  mastery: "text-forge-muted   border-forge-border",
  default: "text-forge-muted   border-forge-border",
};

export function Badge({
  variant = "default",
  children,
}: {
  variant?: BadgeVariant;
  children: ReactNode;
}) {
  return (
    <span
      className={clsx(
        "inline-block font-mono text-[11px] uppercase tracking-widest px-2 py-0.5 rounded-sm border",
        BADGE_STYLES[variant]
      )}
    >
      {children}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Risk bar
// ---------------------------------------------------------------------------

const RISK_BAR_COLORS: Record<RiskLevel, { fill: string; track: string }> = {
  safe:      { fill: "bg-forge-green",  track: "bg-forge-green/15" },
  moderate:  { fill: "bg-forge-amber",  track: "bg-forge-amber/15" },
  dangerous: { fill: "bg-forge-red",    track: "bg-forge-red/15"   },
  critical:  { fill: "bg-red-400",      track: "bg-red-400/15"     },
};

export function RiskBar({
  pct,
  level,
  label,
}: {
  pct: number;
  level: RiskLevel;
  label?: string;
}) {
  const colors = RISK_BAR_COLORS[level];
  return (
    <div>
      {label && (
        <div className="flex justify-between font-mono text-[11px] uppercase tracking-widest text-forge-dim mb-1.5">
          <span>{label}</span>
          <span
            className={clsx(
              level === "safe"      && "text-forge-green",
              level === "moderate"  && "text-forge-amber",
              (level === "dangerous" || level === "critical") && "text-forge-red"
            )}
          >
            {pct.toFixed(1)}%
          </span>
        </div>
      )}
      <div className={clsx("h-2 rounded-full overflow-hidden", colors.track)}>
        <div
          className={clsx("h-full rounded-full transition-all duration-300", colors.fill)}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Spinner
// ---------------------------------------------------------------------------

export function Spinner({ size = 20 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      className="animate-spin text-forge-cyan"
    >
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="2"
        strokeDasharray="40"
        strokeDashoffset="10"
        strokeLinecap="round"
      />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="font-display text-lg text-forge-muted mb-2">{title}</div>
      {description && (
        <p className="font-body text-sm text-forge-dim italic mb-5 max-w-xs leading-relaxed">
          {description}
        </p>
      )}
      {action}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Section label
// ---------------------------------------------------------------------------

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <div className="font-mono text-[11px] uppercase tracking-widest text-forge-cyan/70 mb-3">
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Divider
// ---------------------------------------------------------------------------

export function Divider({ label }: { label?: string }) {
  if (!label) return <hr className="border-forge-border my-4" />;
  return (
    <div className="flex items-center gap-3 my-4">
      <div className="flex-1 h-px bg-forge-border" />
      <span className="font-mono text-[11px] uppercase tracking-widest text-forge-dim">
        {label}
      </span>
      <div className="flex-1 h-px bg-forge-border" />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Confirm Modal — used before destructive actions (delete)
// ---------------------------------------------------------------------------

export function ConfirmModal({
  title,
  message,
  confirmLabel = "Delete",
  onConfirm,
  onCancel,
  isPending = false,
}: {
  title: string;
  message: string;
  confirmLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  isPending?: boolean;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ background: "rgba(0,0,0,0.85)" }}
      onClick={(e) => e.target === e.currentTarget && onCancel()}
    >
      <div className="bg-forge-surface border border-forge-red/50 rounded w-full max-w-sm mx-4 overflow-hidden shadow-2xl">
        <div className="px-5 py-4 border-b border-forge-border bg-forge-surface2 flex items-center justify-between">
          <span className="font-display text-base font-semibold text-forge-red tracking-wider">
            {title}
          </span>
          <button
            onClick={onCancel}
            className="text-forge-dim hover:text-forge-text font-mono text-xl bg-transparent border-none cursor-pointer transition-colors leading-none"
          >
            ×
          </button>
        </div>
        <div className="px-5 py-5">
          <p className="font-body text-sm text-forge-muted leading-relaxed">{message}</p>
        </div>
        <div className="flex justify-end gap-2 px-5 py-4 border-t border-forge-border bg-forge-surface2">
          <Button variant="outline" size="sm" onClick={onCancel} disabled={isPending}>
            Cancel
          </Button>
          <Button variant="danger" size="sm" onClick={onConfirm} disabled={isPending}>
            {isPending ? "Deleting..." : confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
