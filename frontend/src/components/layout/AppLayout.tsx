import { Outlet, NavLink, useNavigate, Link } from "react-router-dom";
import { useAuthStore } from "@/store";

const NAV_LINKS = [
  { to: "/builds",  label: "Builds"   },
  { to: "/build",   label: "Planner"  },
  { to: "/craft",   label: "Craft Sim"},
  { to: "/affixes", label: "Affixes"  },
];

export default function AppLayout() {
  const authUrl = `${import.meta.env.VITE_API_URL ?? "/api"}/auth/discord`;
  const devLoginUrl = `${import.meta.env.VITE_API_URL ?? "/api"}/auth/dev-login`;
  const isDev = import.meta.env.DEV;
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="min-h-screen bg-forge-bg text-forge-text font-body overflow-x-hidden">
      {/* Nav */}
      <nav
        className="sticky top-0 z-50 border-b border-forge-border bg-forge-surface/95 backdrop-blur-md"
        style={{ boxShadow: "0 1px 20px rgba(0,0,0,0.60)" }}
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

          {/* Logo */}
          <NavLink to="/" className="flex items-center gap-3 no-underline group">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <path
                d="M14 2 L24 8 L24 20 L14 26 L4 20 L4 8 Z"
                stroke="#f0a020"
                strokeWidth="1.2"
                fill="rgba(240,160,32,0.07)"
              />
              <path
                d="M14 9 L19 14 L14 21 L9 14 Z"
                fill="#f0a020"
                opacity="0.85"
              />
              <circle cx="14" cy="14" r="2.5" fill="#ffb83f" />
              <circle cx="14" cy="14" r="5" fill="none" stroke="#f0a020" strokeWidth="0.5" opacity="0.4" />
            </svg>
            <span
              className="font-display text-lg font-bold tracking-[0.18em] text-forge-amber group-hover:text-forge-amber-hot transition-colors"
              style={{ textShadow: "0 0 20px rgba(240,160,32,0.35)" }}
            >
              THE FORGE
            </span>
          </NavLink>

          {/* Nav links */}
          <ul className="flex items-center gap-1 list-none">
            {NAV_LINKS.map(({ to, label }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  className={({ isActive }) =>
                    `font-mono text-xs tracking-widest uppercase transition-all no-underline px-3 py-2 rounded-sm ${
                      isActive
                        ? "text-forge-cyan bg-forge-cyan/8 border border-forge-cyan/30"
                        : "text-forge-muted hover:text-forge-text hover:bg-forge-surface2"
                    }`
                  }
                >
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>

          {/* Auth */}
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <Link to="/profile" className="flex items-center gap-2.5 no-underline group">
                  {user.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.username}
                      className="h-8 w-8 rounded-full border border-forge-border group-hover:border-forge-amber transition-colors"
                      style={{ boxShadow: "0 0 8px rgba(240,160,32,0)" }}
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full border border-forge-border bg-forge-surface3 flex items-center justify-center group-hover:border-forge-amber transition-colors">
                      <span className="font-display text-xs font-bold text-forge-amber">
                        {user.username[0].toUpperCase()}
                      </span>
                    </div>
                  )}
                  <span className="font-mono text-xs text-forge-muted group-hover:text-forge-amber transition-colors">
                    {user.username}
                  </span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="font-mono text-xs uppercase tracking-widest text-forge-dim hover:text-forge-red transition-colors border-none bg-transparent cursor-pointer"
                >
                  Logout
                </button>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <a
                  href={authUrl}
                  className="font-display text-xs font-bold tracking-widest uppercase bg-forge-amber text-forge-bg px-4 py-2 rounded-sm hover:bg-forge-amber-hot hover:shadow-glow-amber transition-all no-underline"
                >
                  Sign In
                </a>
                {isDev && (
                  <a
                    href={devLoginUrl}
                    className="font-mono text-xs uppercase tracking-widest text-forge-dim hover:text-forge-amber transition-colors border border-forge-border px-3 py-2 rounded-sm no-underline"
                    title="Dev login (bypasses Discord — development only)"
                  >
                    Dev
                  </a>
                )}
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Page content */}
      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
