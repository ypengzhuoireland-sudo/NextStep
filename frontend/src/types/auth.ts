export interface StudentUser {
  id: string;
  name: string;
  email: string;
  avatarInitials: string;
}

export interface StudentAuthResult {
  token: string;
  user: StudentUser;
}
