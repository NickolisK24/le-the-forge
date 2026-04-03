import { Toaster } from "react-hot-toast";
import toast from "react-hot-toast";

const forgeStyle = {
  style: {
    background: "#10152a",
    color: "#c8d0e0",
    border: "1px solid #2a3050",
    fontFamily: "var(--font-body, sans-serif)",
    fontSize: "14px",
    borderRadius: "2px",
  },
};

export const notify = {
  success: (msg: string, opts?: object) =>
    toast.success(msg, {
      ...forgeStyle,
      iconTheme: { primary: "#4ade80", secondary: "#10152a" },
      ...opts,
    }),
  error: (msg: string, opts?: object) =>
    toast.error(msg, {
      ...forgeStyle,
      iconTheme: { primary: "#ef4444", secondary: "#10152a" },
      ...opts,
    }),
  warning: (msg: string, opts?: object) =>
    toast(msg, { ...forgeStyle, icon: "⚠", ...opts }),
  info: (msg: string, opts?: object) =>
    toast(msg, { ...forgeStyle, icon: "ℹ", ...opts }),
};

export function NotificationCenter() {
  return (
    <Toaster
      position="bottom-right"
      gutter={8}
      toastOptions={{
        duration: 4000,
        style: forgeStyle.style,
        success: {
          iconTheme: { primary: "#4ade80", secondary: "#10152a" },
        },
        error: {
          iconTheme: { primary: "#ef4444", secondary: "#10152a" },
          duration: 6000,
        },
      }}
    />
  );
}
