export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: "student" | "teacher";
}

export interface AuthResult {
  token: string;
  user: AuthUser;
}

export interface StudentUser {
  id: string;
  name: string;
  email: string;
  avatarInitials: string;
  needsDiagnostic: boolean;
  role: "student" | "teacher";
}

export interface StudentAuthResult {
  token: string;
  user: StudentUser;
}
