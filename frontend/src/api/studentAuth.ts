import { apiRequest, AUTH_TOKEN_KEY } from "@/api/client";
import type { StudentAuthResult, StudentUser } from "@/types/auth";

const USER_KEY = "nextstep_student_user";

interface LoginArgs {
  email: string;
  password: string;
  name?: string;
}

interface StudentMeResponse {
  user: StudentUser;
}

export async function loginStudent(
  args: LoginArgs
): Promise<StudentAuthResult> {
  const result = await apiRequest<StudentAuthResult>(
    "/auth/student/login",
    {
      method: "POST",
      body: JSON.stringify({
        email: args.email.trim().toLowerCase(),
        password: args.password
      })
    }
  );

  saveSession(result);
  return result;
}

export async function loginTeacher(
  args: LoginArgs
): Promise<StudentAuthResult> {
  const result = await apiRequest<StudentAuthResult>(
    "/auth/teacher/login",
    {
      method: "POST",
      body: JSON.stringify({
        email: args.email.trim().toLowerCase(),
        password: args.password
      })
    }
  );

  saveSession(result);
  return result;
}

export async function registerStudent(
  args: LoginArgs
): Promise<StudentAuthResult> {
  const result = await apiRequest<StudentAuthResult>(
    "/auth/student/register",
    {
      method: "POST",
      body: JSON.stringify({
        name: args.name?.trim() || "New Student",
        email: args.email.trim().toLowerCase(),
        password: args.password
      })
    }
  );

  saveSession(result);
  return result;
}

export async function getStudentMe(): Promise<StudentUser | null> {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);

  if (!token) {
    return null;
  }

  try {
    const response = await apiRequest<StudentMeResponse>(
      "/auth/student/me"
    );

    localStorage.setItem(
      USER_KEY,
      JSON.stringify(response.user)
    );

    return response.user;
  } catch {
    clearSession();
    return null;
  }
}

export async function logoutStudent(): Promise<void> {
  try {
    await apiRequest<{ message: string }>(
      "/auth/student/logout",
      {
        method: "POST"
      }
    );
  } finally {
    clearSession();
  }
}

function saveSession(result: StudentAuthResult): void {
  localStorage.setItem(AUTH_TOKEN_KEY, result.token);
  localStorage.setItem(
    USER_KEY,
    JSON.stringify(result.user)
  );
}

function clearSession(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
