import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/store";
import { versionApi } from "@/lib/api";

interface TopBarProps {
  onSearchOpen?: () => void;
  onSidebarToggle?: () => void;
  saveStatus?: "idle" | "saving" | "saved" | "error";
  buildName?: string;
}

function HamburgerIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <path d="M3 5 L17 5" />
      <path d="M3 10 L17 10" />
      <path d="M3 15 L17 15" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="6.5" cy="6.5" r="4.5" />
      <path d="M12 12 L14.5 14.5" strokeWidth="2" />
    </svg>
  );
}

function SaveIdleIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12 L2 3 Q2 2 3 2 L9 2 L12 5 L12 12 Q12 12 11 12 L3 12 Q2 12 2 12 Z" />
      <rect x="4" y="2" width="4" height="3.5" />
      <rect x="3.5" y="7.5" width="7" height="4" />
    </svg>
  );
}

function SaveStatusIndicator({ status }: { status: TopBarProps["saveStatus"] }) {
  if (!status || status === "idle") return null;

  const config = {
    saving: { color: "text-forge-amber", label: "Saving..." },
    saved:  { color: "text-forge-green",  label: "Saved" },
    error:  { color: "text-forge-red",    label: "Error" },
  } as const;

  const cfg = config[status as keyof typeof config];
  if (!cfg) return null;

  return (
    <div className={`flex items-center gap-1.5 font-mono text-xs ${cfg.color}`}>
      {status === "saving" ? (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" className="animate-spin" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" strokeDasharray="40" strokeDashoffset="10" strokeLinecap="round" />
        </svg>
      ) : (
        <SaveIdleIcon />
      )}
      <span>{cfg.label}</span>
    </div>
  );
}

export default function TopBar({ onSearchOpen, onSidebarToggle, saveStatus, buildName }: TopBarProps) {
  const authUrl = `${import.meta.env.VITE_API_URL ?? "/api"}/auth/discord`;
  const devLoginUrl = `${import.meta.env.VITE_API_URL ?? "/api"}/auth/dev-login`;
  const isDev = import.meta.env.DEV;
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const { data: versionRes } = useQuery({
    queryKey: ["version"],
    queryFn: () => versionApi.get(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
  const version = versionRes?.data;

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header
      className="sticky top-0 z-40 flex items-center border-b border-forge-border bg-forge-surface/95 backdrop-blur-md shrink-0"
      style={{ height: 56, boxShadow: "0 1px 20px rgba(0,0,0,0.60)" }}
    >
      {/* Left: hamburger + logo */}
      <div className="flex items-center gap-2 px-3">
        {onSidebarToggle && (
          <button
            onClick={onSidebarToggle}
            className="flex items-center justify-center w-9 h-9 rounded-sm text-forge-dim hover:text-forge-text hover:bg-forge-surface2 bg-transparent border-none cursor-pointer transition-colors"
            title="Toggle sidebar"
          >
            <HamburgerIcon />
          </button>
        )}

        <Link to="/" className="flex items-center gap-2 no-underline group">
          <svg width="24" height="24" viewBox="0 0 28 28" fill="none">
            <path
              d="M14 2 L24 8 L24 20 L14 26 L4 20 L4 8 Z"
              stroke="#f0a020"
              strokeWidth="1.2"
              fill="rgba(240,160,32,0.07)"
            />
            <path d="M14 9 L19 14 L14 21 L9 14 Z" fill="#f0a020" opacity="0.85" />
            <circle cx="14" cy="14" r="2.5" fill="#ffb83f" />
            <circle cx="14" cy="14" r="5" fill="none" stroke="#f0a020" strokeWidth="0.5" opacity="0.4" />
          </svg>
          <span
            className="font-display text-sm font-bold tracking-[0.18em] text-forge-amber group-hover:text-forge-amber-hot transition-colors hidden sm:block"
            style={{ textShadow: "0 0 20px rgba(240,160,32,0.35)" }}
          >
            THE FORGE
          </span>
        </Link>

        {version?.version && version.version !== "0.0.0" && (
          <span className="font-mono text-[10px] text-forge-dim hidden lg:block ml-1">
            v{version.version}
          </span>
        )}
      </div>

      {/* Center: search trigger */}
      <div className="flex-1 flex items-center justify-center px-4">
        <button
          onClick={onSearchOpen}
          className="flex items-center gap-2 text-forge-dim hover:text-forge-muted bg-forge-surface2 hover:bg-forge-surface3 border border-forge-border hover:border-forge-border/80 rounded-sm px-3 py-1.5 w-full max-w-xs transition-all cursor-pointer"
        >
          <SearchIcon />
          <span className="font-mono text-xs text-forge-dim flex-1 text-left">Search…</span>
          <kbd className="font-mono text-[10px] text-forge-dim border border-forge-border rounded px-1 py-0.5 hidden sm:block">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Right: save status + build name + auth */}
      <div className="flex items-center gap-3 px-4 shrink-0">
        {buildName && (
          <span className="font-mono text-xs text-forge-muted hidden md:block truncate max-w-[140px]">
            {buildName}
          </span>
        )}

        <SaveStatusIndicator status={saveStatus} />

        {user ? (
          <div className="flex items-center gap-2">
            <Link to="/profile" className="flex items-center gap-2 no-underline group">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.username}
                  className="h-7 w-7 rounded-full border border-forge-border group-hover:border-forge-amber transition-colors"
                />
              ) : (
                <div className="h-7 w-7 rounded-full border border-forge-border bg-forge-surface3 flex items-center justify-center group-hover:border-forge-amber transition-colors">
                  <span className="font-display text-[11px] font-bold text-forge-amber">
                    {user.username[0].toUpperCase()}
                  </span>
                </div>
              )}
              <span className="font-mono text-xs text-forge-muted group-hover:text-forge-amber transition-colors hidden md:block">
                {user.username}
              </span>
            </Link>
            <button
              onClick={handleLogout}
              className="font-mono text-xs uppercase tracking-widest text-forge-dim hover:text-forge-red transition-colors border-none bg-transparent cursor-pointer"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <a
              href={authUrl}
              onClick={() => sessionStorage.setItem("forge_login_attempted", "1")}
              className="font-display text-xs font-bold tracking-widest uppercase bg-forge-amber text-forge-bg px-3 py-1.5 rounded-sm hover:bg-forge-amber-hot hover:shadow-glow-amber transition-all no-underline"
            >
              Sign In
            </a>
            {isDev && (
              <a
                href={devLoginUrl}
                className="font-mono text-xs uppercase tracking-widest text-forge-dim hover:text-forge-amber transition-colors border border-forge-border px-2 py-1.5 rounded-sm no-underline"
                title="Dev login (bypasses Discord)"
              >
                Dev
              </a>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
