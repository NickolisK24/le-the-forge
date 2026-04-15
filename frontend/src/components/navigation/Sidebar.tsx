import { useLocation, NavLink } from "react-router-dom";
import { useEffect, useState } from "react";
import { clsx } from "clsx";

export const SIDEBAR_WIDTH_COLLAPSED = 56;
export const SIDEBAR_WIDTH_EXPANDED = 200;

const STORAGE_KEY = "forge_sidebar_open";

interface SidebarProps {
  /** Mobile-only drawer open state. Ignored above the `md` breakpoint. */
  mobileOpen?: boolean;
  /** Called when a NavLink is tapped while the mobile drawer is open. */
  onMobileNavigate?: () => void;
}

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
}

function DashboardIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="2" width="7" height="7" rx="1" />
      <rect x="11" y="2" width="7" height="7" rx="1" />
      <rect x="2" y="11" width="7" height="7" rx="1" />
      <rect x="11" y="11" width="7" height="7" rx="1" />
    </svg>
  );
}

function BuildPlannerIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 10 L10 3 L17 10 L14 10 L14 17 L6 17 L6 10 Z" />
      <circle cx="10" cy="10" r="2" />
    </svg>
  );
}

function CraftingLabIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 3 L13 3 L16 7 L10 18 L4 7 Z" />
      <path d="M7 3 L10 8 L13 3" />
      <path d="M4 7 L16 7" />
    </svg>
  );
}

function BisSearchIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="8.5" cy="8.5" r="5.5" />
      <path d="M15.5 15.5 L18 18" strokeWidth="2" />
      <path d="M6 8.5 L11 8.5" />
      <path d="M8.5 6 L8.5 11" />
    </svg>
  );
}

function SimulationIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 14 L6 9 L9 12 L13 6 L18 10" />
      <path d="M2 18 L18 18" />
      <circle cx="6" cy="9" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="13" cy="6" r="1.5" fill="currentColor" stroke="none" />
    </svg>
  );
}

function DataManagerIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx="10" cy="5" rx="7" ry="2.5" />
      <path d="M3 5 L3 10 Q3 12.5 10 12.5 Q17 12.5 17 10 L17 5" />
      <path d="M3 10 L3 15 Q3 17.5 10 17.5 Q17 17.5 17 15 L17 10" />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="10" cy="10" r="3" />
      <path d="M10 2 L10 4" />
      <path d="M10 16 L10 18" />
      <path d="M2 10 L4 10" />
      <path d="M16 10 L18 10" />
      <path d="M4.22 4.22 L5.64 5.64" />
      <path d="M14.36 14.36 L15.78 15.78" />
      <path d="M15.78 4.22 L14.36 5.64" />
      <path d="M5.64 14.36 L4.22 15.78" />
    </svg>
  );
}

function BuildsIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="14" height="14" rx="2" />
      <path d="M3 8 L17 8" />
      <path d="M8 8 L8 17" />
    </svg>
  );
}

function PassiveTreeIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="10" cy="4" r="2" />
      <circle cx="5" cy="11" r="2" />
      <circle cx="15" cy="11" r="2" />
      <circle cx="10" cy="17" r="2" />
      <path d="M10 6 L5 9" />
      <path d="M10 6 L15 9" />
      <path d="M5 13 L10 15" />
      <path d="M15 13 L10 15" />
    </svg>
  );
}

function ClassesIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="10" cy="7" r="3" />
      <path d="M4 17 C4 13.5 7 12 10 12 C13 12 16 13.5 16 17" />
    </svg>
  );
}

function MetaIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 17 L3 10 L7 10 L7 17" />
      <path d="M8 17 L8 6 L12 6 L12 17" />
      <path d="M13 17 L13 3 L17 3 L17 17" />
      <path d="M2 17 L18 17" />
    </svg>
  );
}

function ChevronRightIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M6 4 L10 8 L6 12" />
    </svg>
  );
}

function ForgeLogoSmall() {
  return (
    <svg width="24" height="24" viewBox="0 0 28 28" fill="none">
      <path d="M14 2 L24 8 L24 20 L14 26 L4 20 L4 8 Z" stroke="#f0a020" strokeWidth="1.2" fill="rgba(240,160,32,0.07)" />
      <path d="M14 9 L19 14 L14 21 L9 14 Z" fill="#f0a020" opacity="0.85" />
      <circle cx="14" cy="14" r="2.5" fill="#ffb83f" />
    </svg>
  );
}

const NAV_ITEMS: NavItem[] = [
  { to: "/",            label: "Dashboard",     icon: <DashboardIcon /> },
  { to: "/classes",     label: "Classes",       icon: <ClassesIcon /> },
  { to: "/builds",      label: "Builds",        icon: <BuildsIcon /> },
  { to: "/build",       label: "Build Planner", icon: <BuildPlannerIcon /> },
  { to: "/passives",    label: "Passive Tree",  icon: <PassiveTreeIcon /> },
  { to: "/craft",       label: "Crafting Lab",  icon: <CraftingLabIcon /> },
  { to: "/bis-search",  label: "BIS Search",    icon: <BisSearchIcon /> },
  { to: "/encounter",   label: "Simulation",    icon: <SimulationIcon /> },
  { to: "/meta",        label: "Meta",          icon: <MetaIcon /> },
  { to: "/profile",     label: "Profile",       icon: <SettingsIcon /> },
];

// Suppress unused-import warning while keeping the icon around for the
// Data Manager power-user route (still accessible via /data-manager URL).
void DataManagerIcon;

export default function Sidebar({ mobileOpen = false, onMobileNavigate }: SidebarProps = {}) {
  const location = useLocation();
  const [expanded, setExpanded] = useState<boolean>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored === null ? false : stored === "true";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, String(expanded));
    } catch {
      // ignore
    }
  }, [expanded]);

  // Labels are visible whenever they fit:
  //   - Mobile drawer width (w-72 = 288px) — always show.
  //   - Desktop expanded (md:w-[200px]) — show.
  //   - Desktop collapsed (md:w-[56px]) — hide via `md:hidden`.
  // Tailwind classes (rather than `expanded && ...`) keep the DOM stable
  // across breakpoints so the drawer doesn't rerender on resize.
  const labelHideOnDesktop = expanded ? "" : "md:hidden";

  return (
    <aside
      className={clsx(
        "flex flex-col border-r border-forge-border bg-forge-surface overflow-hidden",
        // Mobile: fixed-position drawer with slide-in transform
        "fixed inset-y-0 left-0 z-50 w-72 transform transition-all duration-200",
        mobileOpen ? "translate-x-0" : "-translate-x-full",
        // Desktop (md+): normal flex child, no transform, width follows expanded state
        "md:relative md:translate-x-0 md:shrink-0",
        expanded ? "md:w-[200px]" : "md:w-[56px]",
      )}
    >
      {/* Logo area */}
      <div
        className="flex items-center border-b border-forge-border shrink-0"
        style={{ height: 56, minHeight: 56 }}
      >
        <div className="flex items-center justify-center" style={{ width: SIDEBAR_WIDTH_COLLAPSED }}>
          <ForgeLogoSmall />
        </div>
        <span className={clsx("flex items-center gap-2 overflow-hidden", labelHideOnDesktop)}>
          <span
            className="font-display text-sm font-bold tracking-[0.18em] text-forge-amber whitespace-nowrap"
            style={{ textShadow: "0 0 20px rgba(240,160,32,0.35)" }}
          >
            THE FORGE
          </span>
          <span
            className="font-mono text-[9px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded-sm border border-forge-cyan/40 bg-forge-cyan/12 text-forge-cyan whitespace-nowrap"
            title="Public beta — expect rough edges"
          >
            BETA
          </span>
        </span>
      </div>

      {/* Nav items */}
      <nav className="flex-1 py-2 overflow-y-auto overflow-x-hidden">
        {NAV_ITEMS.map(({ to, label, icon }) => {
          const isActive =
            to === "/" ? location.pathname === "/" : location.pathname.startsWith(to);

          return (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              title={!expanded ? label : undefined}
              onClick={() => onMobileNavigate?.()}
              className="flex items-center no-underline transition-all duration-150 group relative min-h-[44px]"
              style={{
                paddingLeft: 0,
              }}
            >
              {/* Active indicator bar */}
              <div
                className="absolute left-0 top-0 bottom-0 w-0.5 transition-colors duration-150"
                style={{ background: isActive ? "#f0a020" : "transparent" }}
              />

              {/* Icon cell */}
              <div
                className={`flex items-center justify-center transition-colors duration-150 ${
                  isActive
                    ? "text-forge-amber"
                    : "text-forge-dim group-hover:text-forge-muted"
                }`}
                style={{
                  width: SIDEBAR_WIDTH_COLLAPSED,
                  minWidth: SIDEBAR_WIDTH_COLLAPSED,
                  background: isActive ? "rgba(240,160,32,0.07)" : undefined,
                }}
              >
                {icon}
              </div>

              {/* Label */}
              <span
                className={clsx(
                  "font-body text-sm whitespace-nowrap transition-colors duration-150",
                  isActive
                    ? "text-forge-amber font-medium"
                    : "text-forge-muted group-hover:text-forge-text",
                  labelHideOnDesktop,
                )}
              >
                {label}
              </span>
            </NavLink>
          );
        })}
      </nav>

      {/* Expand/collapse toggle — desktop only (mobile uses backdrop tap to close) */}
      <div className="border-t border-forge-border shrink-0 hidden md:block">
        <button
          onClick={() => setExpanded((v) => !v)}
          className="flex items-center w-full text-forge-dim hover:text-forge-muted bg-transparent border-none cursor-pointer transition-colors duration-150 min-h-[44px]"
          title={expanded ? "Collapse sidebar" : "Expand sidebar"}
        >
          <div
            className="flex items-center justify-center"
            style={{ width: SIDEBAR_WIDTH_COLLAPSED, minWidth: SIDEBAR_WIDTH_COLLAPSED }}
          >
            <span
              className="transition-transform duration-200"
              style={{ transform: expanded ? "rotate(180deg)" : "rotate(0deg)" }}
            >
              <ChevronRightIcon />
            </span>
          </div>
          <span
            className={clsx(
              "font-mono text-xs uppercase tracking-widest whitespace-nowrap",
              labelHideOnDesktop,
            )}
          >
            Collapse
          </span>
        </button>
      </div>
    </aside>
  );
}
