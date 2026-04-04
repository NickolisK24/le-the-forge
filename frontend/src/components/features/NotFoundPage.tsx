import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center py-32 gap-4 text-center">
      <div className="font-mono text-6xl text-forge-border">404</div>
      <h1 className="font-display text-forge-amber text-2xl">Page not found</h1>
      <p className="font-body text-forge-dim text-sm max-w-xs">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link
        to="/"
        className="mt-2 font-body text-sm text-forge-amber border border-forge-amber/30 px-4 py-2 rounded hover:bg-forge-amber/10 transition-colors"
      >
        Back to home
      </Link>
    </div>
  );
}
