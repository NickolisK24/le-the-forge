import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-forge-bg flex items-center justify-center p-8">
          <div className="bg-forge-surface border border-red-800/50 rounded p-8 max-w-md w-full text-center">
            <div className="text-red-400 text-4xl mb-4">⚠</div>
            <h1 className="font-display text-forge-amber text-xl mb-2">Something went wrong</h1>
            <p className="font-body text-forge-dim text-sm mb-6">{this.state.message}</p>
            <button
              className="bg-forge-amber/10 border border-forge-amber/30 text-forge-amber font-body text-sm px-4 py-2 rounded hover:bg-forge-amber/20 transition-colors"
              onClick={() => window.location.reload()}
            >
              Reload page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
