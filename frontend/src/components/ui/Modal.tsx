import { useEffect, type ReactNode } from "react";
import { createPortal } from "react-dom";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: "sm" | "md" | "lg" | "xl";
  children: ReactNode;
}

const SIZE_WIDTHS: Record<NonNullable<ModalProps["size"]>, number> = {
  sm: 400,
  md: 560,
  lg: 720,
  xl: 900,
};

export function Modal({ isOpen, onClose, title, size = "md", children }: ModalProps) {
  const maxWidth = SIZE_WIDTHS[size];

  // Escape key closes
  useEffect(() => {
    if (!isOpen) return;
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isOpen, onClose]);

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  const modal = (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{
        background: "rgba(0,0,0,0.80)",
        backdropFilter: "blur(4px)",
        opacity: isOpen ? 1 : 0,
        pointerEvents: isOpen ? "auto" : "none",
        transition: "opacity 150ms ease",
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="bg-forge-surface border border-forge-border rounded w-full overflow-hidden shadow-2xl flex flex-col"
        style={{
          maxWidth,
          maxHeight: "90vh",
          transform: isOpen ? "scale(1)" : "scale(0.97)",
          transition: "transform 150ms ease, opacity 150ms ease",
          opacity: isOpen ? 1 : 0,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between border-b border-forge-border bg-forge-surface2 px-5 py-3.5 shrink-0">
            <span className="font-display text-sm font-bold tracking-wider text-forge-text">
              {title}
            </span>
            <button
              onClick={onClose}
              className="text-forge-dim hover:text-forge-text font-mono text-xl bg-transparent border-none cursor-pointer transition-colors leading-none"
              aria-label="Close"
            >
              ×
            </button>
          </div>
        )}

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-5 min-h-0">
          {children}
        </div>
      </div>
    </div>
  );

  return createPortal(modal, document.body);
}

export function ModalFooter({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-center justify-end gap-2 border-t border-forge-border bg-forge-surface2 px-5 py-3.5 shrink-0 -mx-5 -mb-5 mt-4">
      {children}
    </div>
  );
}
