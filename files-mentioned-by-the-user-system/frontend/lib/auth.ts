export type UserRole = "teacher" | "student" | "admin";
export type UserStatus = "pending_verification" | "active" | "disabled";

export type AuthUser = {
  id: string;
  email: string;
  role: UserRole;
  display_name: string;
  status: UserStatus;
  email_verified_at: string | null;
  created_at: string;
};

export type AuthTokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  user: AuthUser;
};

export type RegistrationResponse = {
  message: string;
  email: string;
  verification_required: boolean;
  verification_token: string | null;
};

export type MessageResponse = {
  message: string;
};

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export function saveAuthSession(result: AuthTokenResponse) {
  window.localStorage.setItem("access_token", result.access_token);
  window.localStorage.setItem("refresh_token", result.refresh_token);
  window.localStorage.setItem("auth_user", JSON.stringify(result.user));
}

export function clearAuthSession() {
  window.localStorage.removeItem("access_token");
  window.localStorage.removeItem("refresh_token");
  window.localStorage.removeItem("auth_user");
}

export function getAccessToken() {
  return window.localStorage.getItem("access_token");
}

export async function registerUser(input: {
  role: "teacher" | "student";
  email: string;
  password: string;
  display_name: string;
}) {
  const response = await fetch(`${API_BASE_URL}/auth/register/${input.role}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: input.email,
      password: input.password,
      display_name: input.display_name,
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as RegistrationResponse;
}

export async function loginUser(input: { email: string; password: string }) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  return parseAuthResponse(response);
}

export async function fetchCurrentUser(accessToken: string) {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as AuthUser;
}

export async function verifyEmail(token: string) {
  const response = await fetch(`${API_BASE_URL}/auth/verify-email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as MessageResponse;
}

export async function requestPasswordReset(email: string) {
  const response = await fetch(`${API_BASE_URL}/auth/password-reset/request`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as RegistrationResponse;
}

export async function confirmPasswordReset(input: {
  token: string;
  new_password: string;
}) {
  const response = await fetch(`${API_BASE_URL}/auth/password-reset/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as MessageResponse;
}

async function parseAuthResponse(response: Response) {
  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return (await response.json()) as AuthTokenResponse;
}

async function readErrorMessage(response: Response) {
  try {
    const payload = await response.json();
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
    return "Request failed";
  } catch {
    return "Request failed";
  }
}
