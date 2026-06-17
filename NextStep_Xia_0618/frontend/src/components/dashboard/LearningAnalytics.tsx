import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { Activity, BarChart3, Zap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardPoint } from "@/types/tutor";

interface LearningAnalyticsProps {
  data: DashboardPoint[];
}

export function LearningAnalytics({ data }: LearningAnalyticsProps) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="border-b border-white/10">
        <div>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-cyan-200" />
            Learning Status
          </CardTitle>
          <p className="mt-1 text-xs text-slate-500">Mastery growth, attempts, and hint usage</p>
        </div>
        <div className="hidden items-center gap-2 text-xs text-emerald-100 sm:flex">
          <Zap className="h-3.5 w-3.5" />
          adaptive loop active
        </div>
      </CardHeader>

      <CardContent className="grid gap-4 p-4 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="h-64 min-w-0 rounded-lg border border-white/10 bg-white/[0.035] p-3">
          <div className="mb-3 flex items-center gap-2 text-xs font-medium uppercase text-slate-500">
            <Activity className="h-3.5 w-3.5" />
            Mastery Progress
          </div>
          <ResponsiveContainer width="100%" height="86%">
            <AreaChart data={data} margin={{ left: -18, right: 8, top: 8, bottom: 0 }}>
              <defs>
                <linearGradient id="masteryArea" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#60a5fa" stopOpacity={0.38} />
                  <stop offset="100%" stopColor="#60a5fa" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  background: "rgba(2, 6, 23, 0.95)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8,
                  color: "#e2e8f0"
                }}
              />
              <Area
                type="monotone"
                dataKey="mastery"
                stroke="#67e8f9"
                strokeWidth={2}
                fill="url(#masteryArea)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="h-64 min-w-0 rounded-lg border border-white/10 bg-white/[0.035] p-3">
          <div className="mb-3 text-xs font-medium uppercase text-slate-500">Attempts & Hints</div>
          <ResponsiveContainer width="100%" height="86%">
            <BarChart data={data} margin={{ left: -18, right: 8, top: 8, bottom: 0 }}>
              <CartesianGrid stroke="rgba(148,163,184,0.12)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  background: "rgba(2, 6, 23, 0.95)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8,
                  color: "#e2e8f0"
                }}
              />
              <Bar dataKey="attempts" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              <Bar dataKey="hints" fill="#34d399" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
