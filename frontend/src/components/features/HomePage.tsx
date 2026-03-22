import { Link } from "react-router-dom";
import { Button } from "@/components/ui";

const FEATURES = [
  {
    to: "/build",
    title: "Build Planner",
    description:
      "Full passive tree, skill specialization, and stat sheet in one shareable link. No account needed.",
    status: "Live",
    statusVariant: "live",
    icon: "⚔",
    accentColor: "#f0a020",
  },
  {
    to: "/craft",
    title: "Craft Simulator",
    description:
      "Plan your crafting sequence with FP cost simulation. Find the optimal path to your target item.",
    status: "Live",
    statusVariant: "live",
    icon: "🔥",
    accentColor: "#e06030",
  },
  {
    to: "/builds",
    title: "Community Builds",
    description:
      "Browse and vote on community builds filtered by class, mastery, tier, and playstyle.",
    status: "Live",
    statusVariant: "live",
    icon: "⚡",
    accentColor: "#00d4f5",
  },
];

const STATUS_STYLES: Record<string, string> = {
  live: "text-forge-green border-forge-green/40 bg-forge-green/12",
  beta: "text-forge-cyan border-forge-cyan/40 bg-forge-cyan/8",
  soon: "text-forge-dim border-forge-border",
};

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="py-24 text-center">
        <div className="font-mono text-xs uppercase tracking-[0.28em] text-forge-cyan mb-8 flex items-center justify-center gap-4">
          <span className="block h-px w-10 bg-forge-cyan/50" />
          Last Epoch Community Hub
          <span className="block h-px w-10 bg-forge-cyan/50" />
        </div>

        <h1 className="font-display text-8xl font-bold leading-none tracking-tight text-forge-text mb-2">
          The{" "}
          <span
            className="text-forge-amber block"
            style={{ textShadow: "0 0 40px rgba(240,160,32,0.50), 0 0 80px rgba(240,160,32,0.20)" }}
          >
            Forge
          </span>
        </h1>

        <p className="font-body text-xl font-light text-forge-muted mt-8 max-w-xl mx-auto leading-relaxed">
          Plan builds. Simulate crafts. Browse community builds.
          <br />
          <span className="text-forge-dim text-base">
            The definitive theorycrafting platform for Eterra's finest.
          </span>
        </p>

        <div
          className="h-px w-24 mx-auto my-10"
          style={{ background: "linear-gradient(90deg, transparent, #f0a020, transparent)" }}
        />

        <div className="flex gap-4 justify-center">
          <Link to="/build">
            <Button variant="primary" size="md">Start Planning</Button>
          </Link>
          <Link to="/craft">
            <Button variant="ghost" size="md">Open Simulator</Button>
          </Link>
        </div>
      </section>

      {/* Features grid */}
      <section className="py-8">
        <div className="font-mono text-xs uppercase tracking-[0.28em] text-forge-dim text-center mb-8">
          What The Forge Offers
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {FEATURES.map((f) => (
            <Link
              key={f.to}
              to={f.to}
              className="block no-underline group"
            >
              <div
                className="h-full bg-forge-surface border border-forge-border rounded p-7 transition-all duration-200 relative overflow-hidden
                  hover:border-forge-border-hot hover:-translate-y-0.5"
                style={{
                  background: `linear-gradient(135deg, #0c0f1c 0%, #10152a 100%)`,
                }}
              >
                {/* Accent glow line at top */}
                <div
                  className="absolute top-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  style={{ background: `linear-gradient(90deg, transparent, ${f.accentColor}, transparent)` }}
                />

                <div
                  className="text-3xl mb-5 block"
                  style={{ filter: `drop-shadow(0 0 8px ${f.accentColor}60)` }}
                >
                  {f.icon}
                </div>

                <div className="font-display text-lg font-semibold text-forge-text tracking-wider mb-3">
                  {f.title}
                </div>

                <p className="font-body text-sm text-forge-muted leading-relaxed mb-5">
                  {f.description}
                </p>

                <span
                  className={`inline-block font-mono text-[10px] uppercase tracking-widest px-2 py-1 border rounded-sm ${
                    STATUS_STYLES[f.statusVariant]
                  }`}
                >
                  {f.status}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Bottom tagline */}
      <section className="py-12 text-center">
        <div className="font-mono text-xs text-forge-dim tracking-wider">
          Free to use · No account required · Community driven
        </div>
      </section>
    </div>
  );
}
