/**
 * UI+15 — Smart Tooltip Expansion
 * Rich contextual tooltip with deep data display.
 */

import React, {
  useState,
  useRef,
  useEffect,
  useCallback,
  ReactNode,
} from "react";

export type TooltipPlacement = "top" | "bottom" | "left" | "right" | "auto";

export interface TooltipSection {
  title?: string;
  content: ReactNode;
  variant?: "default" | "warning" | "info" | "success" | "error";
}

interface AdvancedTooltipProps {
  /** Tooltip content — either a simple string or structured sections. */
  content: string | ReactNode | TooltipSection[];
  children: ReactNode;
  placement?: TooltipPlacement;
  /** Delay before showing tooltip, in ms. */
  delay?: number;
  /** Delay before hiding tooltip, in ms. */
  hideDelay?: number;
  /** Maximum width of tooltip in pixels. */
  maxWidth?: number;
  disabled?: boolean;
  className?: string;
  /** Render trigger as inline-block (true) or block (false). */
  inline?: boolean;
}

const VARIANT_STYLES: Record<string, string> = {
  default: "border-[#2d3748]",
  warning: "border-amber-500/50",
  info:    "border-cyan-500/50",
  success: "border-green-500/50",
  error:   "border-red-500/50",
};

const VARIANT_TITLE: Record<string, string> = {
  default: "text-gray-300",
  warning: "text-amber-400",
  info:    "text-cyan-400",
  success: "text-green-400",
  error:   "text-red-400",
};

function isSectionArray(v: unknown): v is TooltipSection[] {
  return Array.isArray(v) && v.length > 0 && typeof v[0] === "object" && v[0] !== null && "content" in v[0];
}

function TooltipContent({ content }: { content: AdvancedTooltipProps["content"] }): React.JSX.Element {
  if (typeof content === "string") {
    return <p className="text-xs text-gray-300">{content}</p>;
  }
  if (isSectionArray(content)) {
    return (
      <div className="space-y-2">
        {content.map((section, i) => (
          <div key={i} className={`${i > 0 ? "pt-2 border-t border-[#2d3748]" : ""}`}>
            {section.title && (
              <div className={`text-[10px] font-semibold uppercase tracking-wider mb-1 ${
                VARIANT_TITLE[section.variant ?? "default"]
              }`}>
                {section.title}
              </div>
            )}
            <div className="text-xs text-gray-300">{section.content}</div>
          </div>
        ))}
      </div>
    );
  }
  return <div className="text-xs text-gray-300">{content as ReactNode}</div>;
}

export function AdvancedTooltip({
  content,
  children,
  placement = "auto",
  delay = 300,
  hideDelay = 100,
  maxWidth = 280,
  disabled = false,
  className = "",
  inline = true,
}: AdvancedTooltipProps): React.JSX.Element {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [actualPlacement, setActualPlacement] = useState<Exclude<TooltipPlacement, "auto">>("top");

  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const showTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const resolvePosition = useCallback(() => {
    const trigger = triggerRef.current;
    const tooltip = tooltipRef.current;
    if (!trigger || !tooltip) return;

    const rect = trigger.getBoundingClientRect();
    const tRect = tooltip.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const gap = 8;

    let place: Exclude<TooltipPlacement, "auto"> =
      placement === "auto" ? "top" : placement;

    // Auto-placement: prefer top, fall back to bottom if not enough space
    if (placement === "auto") {
      if (rect.top < tRect.height + gap) place = "bottom";
      else place = "top";
    }

    let top = 0;
    let left = 0;

    if (place === "top") {
      top = rect.top - tRect.height - gap;
      left = rect.left + rect.width / 2 - tRect.width / 2;
    } else if (place === "bottom") {
      top = rect.bottom + gap;
      left = rect.left + rect.width / 2 - tRect.width / 2;
    } else if (place === "left") {
      top = rect.top + rect.height / 2 - tRect.height / 2;
      left = rect.left - tRect.width - gap;
    } else {
      top = rect.top + rect.height / 2 - tRect.height / 2;
      left = rect.right + gap;
    }

    // Clamp to viewport
    left = Math.max(gap, Math.min(vw - tRect.width - gap, left));
    top  = Math.max(gap, Math.min(vh - tRect.height - gap, top));

    setActualPlacement(place);
    setPosition({ top, left });
  }, [placement]);

  const show = useCallback(() => {
    if (disabled) return;
    if (hideTimer.current) clearTimeout(hideTimer.current);
    showTimer.current = setTimeout(() => {
      setVisible(true);
      requestAnimationFrame(resolvePosition);
    }, delay);
  }, [disabled, delay, resolvePosition]);

  const hide = useCallback(() => {
    if (showTimer.current) clearTimeout(showTimer.current);
    hideTimer.current = setTimeout(() => setVisible(false), hideDelay);
  }, [hideDelay]);

  useEffect(() => {
    if (visible) resolvePosition();
  }, [visible, resolvePosition]);

  useEffect(() => () => {
    if (showTimer.current) clearTimeout(showTimer.current);
    if (hideTimer.current) clearTimeout(hideTimer.current);
  }, []);

  const mainVariant =
    isSectionArray(content) ? content[0]?.variant ?? "default" : "default";

  return (
    <>
      <div
        ref={triggerRef}
        onMouseEnter={show}
        onMouseLeave={hide}
        onFocus={show}
        onBlur={hide}
        className={`${inline ? "inline-block" : "block"} ${className}`}
        aria-describedby={visible ? "adv-tooltip" : undefined}
      >
        {children}
      </div>

      {visible && !disabled && (
        <div
          ref={tooltipRef}
          id="adv-tooltip"
          role="tooltip"
          onMouseEnter={() => hideTimer.current && clearTimeout(hideTimer.current)}
          onMouseLeave={hide}
          className={`fixed z-[9999] rounded-lg border bg-[#0d1117] shadow-xl p-3
                      pointer-events-auto animate-in fade-in duration-150
                      ${VARIANT_STYLES[mainVariant]}`}
          style={{ top: position.top, left: position.left, maxWidth }}
          data-placement={actualPlacement}
        >
          <TooltipContent content={content} />
        </div>
      )}
    </>
  );
}
