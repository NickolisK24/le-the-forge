import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/store";
import { setToken } from "@/lib/api";
import { Spinner } from "@/components/ui";

export default function AuthCallbackPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { login, logout } = useAuthStore();

  useEffect(() => {
    const token = params.get("token");
    if (!token) {
      logout();
      navigate("/");
      return;
    }

    setToken(token);
    authApi.me().then((res) => {
      if (res.data) {
        sessionStorage.setItem("forge_token", token);
        login(token, res.data);
        navigate("/");
      } else {
        logout();
        navigate("/");
      }
    });
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-forge-bg">
      <div className="flex flex-col items-center gap-4">
        <Spinner size={32} />
        <span className="font-mono text-xs uppercase tracking-widest text-forge-muted">
          Authenticating...
        </span>
      </div>
    </div>
  );
}
