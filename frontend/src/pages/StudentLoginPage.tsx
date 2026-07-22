import { FormEvent, useState } from "react";
import { motion } from "framer-motion";
import { BrainCircuit, Loader2, LockKeyhole, Mail, Sparkles } from "lucide-react";
import { loginStudent, loginTeacher, registerStudent } from "@/api/studentAuth";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { StudentUser } from "@/types/auth";
import { cn } from "@/lib/utils";

type Mode = "login" | "register" | "teacher";

interface StudentLoginPageProps {
  onLogin: (user: StudentUser) => void;
}

export function StudentLoginPage({ onLogin }: StudentLoginPageProps) {
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("Python Beginner");
  const [email, setEmail] = useState("student@nextstep.test");
  const [password, setPassword] = useState("demo1234");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr("");

    try {
      const res =
        mode === "login"
          ? await loginStudent({ email, password })
          : mode === "teacher"
            ? await loginTeacher({ email, password })
          : await registerStudent({ name, email, password });
      onLogin(res.user);
    } catch (error) {
      setErr(error instanceof Error ? error.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  function switchMode(nextMode: Mode) {
    setMode(nextMode);
    setErr("");

    if (nextMode === "login") {
      setName("Python Beginner");
      setEmail("student@nextstep.test");
      setPassword("demo1234");
      return;
    }

    if (nextMode === "teacher") {
      setName("");
      setEmail("teacher@nextstep.test");
      setPassword("demo1234");
      return;
    }

    setName("");
    setEmail("");
    setPassword("");
  }

  return (
    <main className="soft-grid grid min-h-screen place-items-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.42, ease: "easeOut" }}
        className="w-full max-w-lg"
      >
        <Card className="overflow-hidden">
          <CardHeader className="border-b border-white/10 p-6">
            <div className="flex items-center gap-3">
              <div className="grid h-12 w-12 place-items-center rounded-lg border border-cyan-300/20 bg-cyan-300/10 shadow-glow">
                <BrainCircuit className="h-6 w-6 text-cyan-100" />
              </div>
              <div>
                <CardTitle className="text-lg">NextStep AI Tutor</CardTitle>
                <p className="mt-1 text-sm text-slate-500">Student practice login</p>
              </div>
            </div>
            <Badge variant="violet">
              <Sparkles className="h-3.5 w-3.5" />
              Adaptive
            </Badge>
          </CardHeader>

          <CardContent className="p-6">
            <div className="mb-5 grid grid-cols-3 gap-2 rounded-lg border border-white/10 bg-white/[0.035] p-1">
              <button type="button" onClick={() => switchMode("login")} className={tabClass(mode === "login")}>
                Login
              </button>
              <button type="button" onClick={() => switchMode("register")} className={tabClass(mode === "register")}>
                Register
              </button>
              <button type="button" onClick={() => switchMode("teacher")} className={tabClass(mode === "teacher")}>
                Teacher
              </button>
            </div>

            <form className="space-y-4" onSubmit={submit}>
              {mode === "register" ? (
                <label className="block">
                  <span className="mb-1.5 block text-xs font-medium uppercase text-slate-500">Student Name</span>
                  <div className="rounded-lg border border-white/10 bg-slate-950/35 px-3">
                    <input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="h-11 w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
                      placeholder="Python Beginner"
                    />
                  </div>
                </label>
              ) : null}

              <label className="block">
                <span className="mb-1.5 block text-xs font-medium uppercase text-slate-500">
                  {mode === "teacher" ? "Teacher Email" : "Student Email"}
                </span>
                <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-slate-950/35 px-3">
                  <Mail className="h-4 w-4 text-slate-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-11 min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
                    placeholder={mode === "teacher" ? "teacher@nextstep.test" : "student@nextstep.test"}
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
                    className="h-11 min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
                    placeholder="Password"
                  />
                </div>
              </label>

              {err ? (
                <div className="rounded-lg border border-rose-300/20 bg-rose-300/[0.08] px-3 py-2 text-xs text-rose-100">
                  {err}
                </div>
              ) : null}

              <Button size="lg" className="mt-2 w-full" disabled={busy || !email || !password}>
                {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                {mode === "register"
                  ? "Create Student Account"
                  : mode === "teacher"
                    ? "Login to Teacher Dashboard"
                    : "Login to Practice"}
              </Button>
            </form>

          </CardContent>
        </Card>
      </motion.div>
    </main>
  );
}

function tabClass(active: boolean) {
  return cn(
    "h-9 rounded-md text-xs font-medium text-slate-400 transition-colors",
    active && "bg-white/[0.08] text-white"
  );
}
