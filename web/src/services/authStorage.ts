const ACCESS_TOKEN_KEY = "cyberguard_access_token";
const REFRESH_TOKEN_KEY = "cyberguard_refresh_token";

export function getAccessToken(): string | null {
  try {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getRefreshToken(): string | null {
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setSession(
  accessToken: string,
  refreshToken: string,
): void {
  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    accessToken,
  );

  localStorage.setItem(
    REFRESH_TOKEN_KEY,
    refreshToken,
  );
}

export function clearSession(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}