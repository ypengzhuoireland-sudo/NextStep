export const AUTH_TOKEN_KEY = "nextstep_student_token";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? "http://127.0.0.1:8000/api" : "/api");

export async function apiRequest<TResponse>(
  path: string,
  options: RequestInit = {}
): Promise<TResponse> {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token
        ? { Authorization: `Bearer ${token}` }
        : {}),
      ...(options.headers ?? {})
    }
  });

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => null);

    throw new Error(
      body?.detail ||
      `Request failed with ${response.status}`
    );
  }

  return response.json() as Promise<TResponse>;
}
