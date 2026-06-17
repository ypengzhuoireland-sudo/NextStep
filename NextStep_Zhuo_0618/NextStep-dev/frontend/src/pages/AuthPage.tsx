import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, Loader2, LockKeyhole, Mail, UserRound } from "lucide-react";
import { loginUser, registerUser } from "@/api/auth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AuthUser } from "@/types/auth";
import { cn } from "@/lib/utils";

type AuthMode = "login" | "register";

interface AuthPageProps {
  onAuthed: (user: AuthUser) => void;
}

export function AuthPage({ onAuthed }: AuthPageProps) {
  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("teacher@nextstep.test");
  const [password, setPassword] = useState("demo1234");
  const [name, setName] = useState("Demo Teacher");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr("");

    try {
      const res =
        mode === "login"
          ? await loginUser({ email, password })
          : await registerUser({ name, email, password });
      onAuthed(res.user);
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Auth failed";
      // older mock errors had JSON-ish text
      setErr(msg.includes("detail") ? msg.replace(/[{}"]/g, "") : msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="soft-grid grid min-h-screen place-items-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.42, ease: "easeOut" }}
        className="w-full max-w-md"
      >
        <Card className="overflow-hidden">
          <CardHeader className="border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="grid h-11 w-11 place-items-center rounded-lg border border-cyan-300/20 bg-cyan-300/10 shadow-glow">
                <BrainCircuit className="h-5 w-5 text-cyan-100" />
              </div>
              <div>
                <CardTitle className="text-base">NextStep</CardTitle>
                <p className="mt-1 text-xs text-slate-500">Teacher access</p>
              </div>
            </div>
            <Badge variant={mode === "login" ? "blue" : "green"}>
              {mode === "login" ? "Login" : "Register"}
            </Badge>
          </CardHeader>

          <CardContent className="p-4">
            <div className="mb-4 grid grid-cols-2 gap-2 rounded-lg border border-white/10 bg-white/[0.035] p-1">
              <button
                type="button"
                onClick={() => setMode("login")}
                className={tabCls(mode === "login")}
              >
                Login
              </button>
              <button
                type="button"
                onClick={() => setMode("register")}
                className={tabCls(mode === "register")}
              >
                Register
              </button>
            </div>

            <form className="space-y-3" onSubmit={submit}>
              {mode === "register" ? (
                <label className="block">
                  <span className="mb-1.5 block text-xs font-medium uppercase text-slate-500">Name</span>
                  <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-slate-950/35 px-3">
                    <UserRound className="h-4 w-4 text-slate-500" />
                    <input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="h-10 min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
                      placeholder="Demo Teacher"
                    />
                  </div>
                </label>
              ) : null}

              <label className="block">
                <span className="mb-1.5 block text-xs font-medium uppercase text-slate-500">Email</span>
                <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-slate-950/35 px-3">
                  <Mail className="h-4 w-4 text-slate-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-10 min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
                    placeholder="teacher@example.com"
                  />
                </div>
              </label>

              <label className="block">
                <span className="mb-1.5 block text-xs font-medium uppercase text-slate-500">Password</span>
                <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-slate-950/35 px-3">
                  <LockKeyhole className="h-4 w-4 text-slate-500" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-10 min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
                    placeholder="Password"
                  />
                </div>
              </label>

              {err ? (
                <div className="rounded-lg border border-rose-300/20 bg-rose-300/[0.08] px-3 py-2 text-xs text-rose-100">
                  {err}
                </div>
              ) : null}

              <Button className="mt-2 w-full" disabled={busy || !email || !password}>
                {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                {mode === "login" ? "Login" : "Create account"}
              </Button>
            </form>

            <p className="mt-4 text-xs leading-5 text-slate-500">
              Demo accounts are saved in browser storage for now.
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </main>
  );
}

function tabCls(active: boolean) {
  return cn(
    "h-8 rounded-md text-xs font-medium text-slate-400 transition-colors",
    active && "bg-white/[0.08] text-white"
  );
}
