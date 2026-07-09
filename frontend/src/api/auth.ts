import { AUTH_TOKEN_KEY } from "@/api/client";
import type { AuthResult, AuthUser } from "@/types/auth";

interface AuthPayload {
  email: string;
  password: string;
  name?: string;
}

interface LocalAccount extends AuthUser {
  password: string;
}

const USERS_KEY = "nextstep_users";

export async function loginUser(payload: AuthPayload) {
  await nap(320);
  const email = payload.email.trim().toLowerCase();
  const account = readUsers().find((user) => user.email === email);

  if (!account || account.password !== payload.password) {
    throw new Error("Invalid email or password");
  }

  return saveSession(account);
}

export async function registerUser(payload: AuthPayload) {
  await nap(420);
  const email = payload.email.trim().toLowerCase();
  const list = readUsers();

  if (list.some((user) => user.email === email)) {
    throw new Error("Email already registered");
  }

  const account: LocalAccount = {
    id: `usr_${Date.now()}`,
    name: payload.name?.trim() || "Demo Teacher",
    email,
    role: "teacher",
    password: payload.password
  };

  localStorage.setItem(USERS_KEY, JSON.stringify([...list, account]));
  return saveSession(account);
}

export async function getMe(): Promise<AuthUser | null> {
  await nap(120);
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (!token) {
    return null;
  }

  // token format is intentionally simple for the frontend-only demo
  const id = token.replace("local_", "");
  const user = readUsers().find((item) => item.id === id);
  return user ? publicUser(user) : null;
}

export function logoutUser() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

function saveSession(account: LocalAccount): AuthResult {
  localStorage.setItem(AUTH_TOKEN_KEY, `local_${account.id}`);
  return {
    token: `local_${account.id}`,
    user: publicUser(account)
  };
}

function readUsers(): LocalAccount[] {
  const saved = localStorage.getItem(USERS_KEY);
  if (!saved) {
    return [demoUser];
  }

  try {
    return JSON.parse(saved) as LocalAccount[];
  } catch {
    // old broken local data, easiest reset for demo
    localStorage.removeItem(USERS_KEY);
    return [demoUser];
  }
}

function publicUser(user: LocalAccount): AuthUser {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    role: user.role
  };
}

const demoUser: LocalAccount = {
  id: "usr_demo_teacher",
  name: "Demo Teacher",
  email: "teacher@nextstep.test",
  role: "teacher",
  password: "demo1234"
};

const nap = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));
