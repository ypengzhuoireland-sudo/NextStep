import { useEffect, useState } from "react";
import { getStudentMe, logoutStudent } from "@/api/studentAuth";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { DiagnosticTestPage } from "@/pages/DiagnosticTestPage";
import { PracticePage } from "@/pages/PracticePage";
import { StudentDashboardPage } from "@/pages/StudentDashboardPage";
import { StudentLoginPage } from "@/pages/StudentLoginPage";
import { TeacherDashboardPage } from "@/pages/TeacherDashboardPage";
import type { StudentUser } from "@/types/auth";

export default function App() {
  const [student, setStudent] = useState<StudentUser | null>(null);
  const [checking, setChecking] = useState(true);
  const [view, setView] = useState<"practice" | "dashboard">("practice");
  const [initialExerciseId, setInitialExerciseId] = useState<string>();

  useEffect(() => {
    let mounted = true;

    async function loadStudent() {
      const user = await getStudentMe();
      if (mounted) {
        setStudent(user);
        if (user?.role === "teacher") {
          setView("dashboard");
        }
        setChecking(false);
      }
    }

    void loadStudent();

    return () => {
      mounted = false;
    };
  }, []);

  async function handleLogout() {
    await logoutStudent();
    setStudent(null);
    setView("practice");
  }

  if (checking) {
    return <LoadingScreen />;
  }

  if (!student) {
    return (
      <StudentLoginPage
        onLogin={(user) => {
          setStudent(user);
          setView(user.role === "teacher" ? "dashboard" : "practice");
        }}
      />
    );
  }

  if (student.role === "student" && student.needsDiagnostic) {
    return (
      <DiagnosticTestPage
        onComplete={(exerciseId) => {
          setInitialExerciseId(exerciseId);
          setStudent({ ...student, needsDiagnostic: false });
          setView("practice");
        }}
      />
    );
  }

  if (view === "dashboard") {
    if (student.role === "teacher") {
      return <TeacherDashboardPage onLogout={handleLogout} />;
    }

    return <StudentDashboardPage onOpenPractice={() => setView("practice")} onLogout={handleLogout} />;
  }

  return (
    <PracticePage
      initialExerciseId={initialExerciseId}
      onOpenDashboard={() => setView("dashboard")}
      onLogout={handleLogout}
      dashboardLabel={student.role === "teacher" ? "Teacher Dashboard" : "Student Dashboard"}
      learnerLabel={student.name}
    />
  );
}
