import { useEffect, useState } from "react";
import { getStudentMe } from "@/api/studentAuth";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { DashboardPage } from "@/pages/DashboardPage";
import { PracticePage } from "@/pages/PracticePage";
import { StudentLoginPage } from "@/pages/StudentLoginPage";
import type { StudentUser } from "@/types/auth";

export default function App() {
  const [student, setStudent] = useState<StudentUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [view, setView] = useState<"practice" | "dashboard">("practice");

  useEffect(() => {
    let mounted = true;

    async function loadStudent() {
      const user = await getStudentMe();
      if (mounted) {
        setStudent(user);
        setChecking(false);
      }
    }

    void loadStudent();

    return () => {
      mounted = false;
    };
  }, []);

  if (checking) {
    return <LoadingScreen />;
  }

  if (!student) {
    return <StudentLoginPage onLogin={setStudent} />;
  }

  if (view === "dashboard") {
    return <DashboardPage onOpenPractice={() => setView("practice")} />;
  }

  return <PracticePage onOpenDashboard={() => setView("dashboard")} />;
}
