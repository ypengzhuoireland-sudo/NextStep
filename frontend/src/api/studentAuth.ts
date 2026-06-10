import type { StudentAuthResult, StudentUser } from "@/types/auth";

const TOKEN_KEY = "nextstep_student_token";
const USER_KEY = "nextstep_student_user";

interface LoginArgs {
  email: string;
  password: string;
  name?: string;
}

const demoStudent = {
  id: "stu_python_beginner_01",
  name: "Python Beginner",
  email: "student@nextstep.test",
  password: "demo1234",
  avatarInitials: "PB"
};

export async function loginStudent(args: LoginArgs): Promise<StudentAuthResult> {
  await sleep(360);

  const email = args.email.trim().toLowerCase();
  const account = readAccounts().find((item) => item.email === email);

  if (!account || account.password !== args.password) {
    throw new Error("Invalid student email or password");
  }

  return saveLogin(account);
}

export async function registerStudent(args: LoginArgs): Promise<StudentAuthResult> {
  await sleep(420);
  const email = args.email.trim().toLowerCase();
  const list = readAccounts();

  if (list.some((item) => item.email === email)) {
    throw new Error("Email already registered");
  }

  const account = {
    id: `stu_local_${Date.now()}`,
    name: args.name?.trim() || "New Student",
    email,
    password: args.password,
    avatarInitials: initials(args.name || email)
  };

  localStorage.setItem("nextstep_student_accounts", JSON.stringify([...list, account]));
  return saveLogin(account);
}

export async function getStudentMe(): Promise<StudentUser | null> {
  await sleep(90);
  const token = localStorage.getItem(TOKEN_KEY);
  const raw = localStorage.getItem(USER_KEY);
  if (!token || !raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as StudentUser;
  } catch {
    // old local test data sometimes breaks this
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function logoutStudent() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function toUser(student: typeof demoStudent): StudentUser {
  return {
    id: student.id,
    name: student.name,
    email: student.email,
    avatarInitials: student.avatarInitials
  };
}

function saveLogin(student: typeof demoStudent): StudentAuthResult {
  const user = toUser(student);
  const token = `student_${student.id}`;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  return { token, user };
}

function readAccounts() {
  const raw = localStorage.getItem("nextstep_student_accounts");
  if (!raw) {
    return [demoStudent];
  }

  try {
    return [demoStudent, ...(JSON.parse(raw) as Array<typeof demoStudent>)];
  } catch {
    localStorage.removeItem("nextstep_student_accounts");
    return [demoStudent];
  }
}

function initials(text: string) {
  return text
    .split(/[\s@._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "ST";
}

const sleep = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));
