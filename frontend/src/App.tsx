import { useState } from "react";
import { DashboardPage } from "@/pages/DashboardPage";
import { PracticePage } from "@/pages/PracticePage";

export default function App() {
  const [view, setView] = useState<"practice" | "dashboard">("practice");

  if (view === "dashboard") {
    return <DashboardPage onOpenPractice={() => setView("practice")} />;
  }

  return <PracticePage onOpenDashboard={() => setView("dashboard")} />;
}
