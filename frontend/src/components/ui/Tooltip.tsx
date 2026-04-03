import { useState, useRef, useCallback, type ReactNode } from "react";
import { createPortal } from "react-dom";

interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  delay?: number;
}

export function Tooltip({ content, children, position = "top", delay = 300 }: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const [coords, setCoords] = useState({ x: 0, y: 0 });
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  const show = useCallback(() => {
    timerRef.current = setTimeout(() => {
      if (!triggerRef.current) return;
      const rect = triggerRef.current.getBoundingClientRect();
      const gap = 8;

      let x = 0;
      let y = 0;

      switch (position) {
        case "top":
          x = rect.left + rect.width / 2;
          y = rect.top - gap;
          break;
        case "bottom":
          x = rect.left + rect.width / 2;
          y = rect.bottom + gap;
          break;
        case "left":
          x = rect.left - gap;
          y = rect.top + rect.height / 2;
          break;
        case "right":
          x = rect.right + gap;
          y = rect.top + rect.height / 2;
          break;
      }

      setCoords({ x, y });
      setVisible(true);
    }, delay);
  }, [position, delay]);

  const hide = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setVisible(false);
  }, []);

  const transformOrigin: Record<typeof position, string> = {
    top:    "translateX(-50%) translateY(-100%)",
    bottom: "translateX(-50%) translateY(0%)",
    left:   "translateX(-100%) translateY(-50%)",
    right:  "translateX(0%) translateY(-50%)",
  };

  const tooltip = visible ? (
    <div
      className="fixed z-[9999] pointer-events-none"
      style={{ left: coords.x, top: coords.y, transform: transformOrigin[position] }}
    >
      <div
        className="bg-forge-surface2 border border-forge-border rounded-sm px-2.5 py-1.5 shadow-lg"
        style={{ maxWidth: 280 }}
      >
        {typeof content === "string" ? (
          <span className="font-body text-xs text-forge-muted">{content}</span>
        ) : (
          content
        )}
      </div>
    </div>
  ) : null;

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={show}
        onMouseLeave={hide}
        onFocus={show}
        onBlur={hide}
        className="inline-block"
      >
        {children}
      </div>
      {tooltip && createPortal(tooltip, document.body)}
    </>
  );
}
