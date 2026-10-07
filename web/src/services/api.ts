const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  console.warn(
    "VITE_API_BASE_URL is not configured.",
  );
}

export type ApiErrorKind =
  | "configuration"
  | "network"
  | "timeout"
  | "validation"
  | "authentication"
  | "forbidden"
  | "not_found"
  | "rate_limit"
  | "server"
  | "unknown";

export class ApiError extends Error {
  status: number;
  data?: unknown;
  kind: ApiErrorKind;

  constructor(
    message: string,
    status: number,
    data?: unknown,
    kind: ApiErrorKind = "unknown",
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
    this.data = data;
    this.kind = kind;
  }
}

interface RequestOptions extends RequestInit {
  token?: string;
  timeoutMs?: number;
}

interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    is_verified: boolean;
  };
}

const ACCESS_TOKEN_KEY =
  "cyberguard_access_token";

const REFRESH_TOKEN_KEY =
  "cyberguard_refresh_token";

const DEFAULT_TIMEOUT_MS = 15_000;

let refreshPromise:
  | Promise<RefreshResponse>
  | null = null;

function getStoredRefreshToken(): string | null {
  try {
    return localStorage.getItem(
      REFRESH_TOKEN_KEY,
    );
  } catch {
    return null;
  }
}

function storeRefreshedSession(
  response: RefreshResponse,
): void {
  try {
    localStorage.setItem(
      ACCESS_TOKEN_KEY,
      response.access_token,
    );

    localStorage.setItem(
      REFRESH_TOKEN_KEY,
      response.refresh_token,
    );
  } catch {
    throw new ApiError(
      "Unable to save the refreshed session.",
      0,
      undefined,
      "configuration",
    );
  }
}

function clearStoredSession(): void {
  try {
    localStorage.removeItem(
      ACCESS_TOKEN_KEY,
    );

    localStorage.removeItem(
      REFRESH_TOKEN_KEY,
    );
  } catch {
    // Ignore storage cleanup failures.
  }
}

function getErrorDetail(
  data: unknown,
): string | null {
  if (
    typeof data === "object" &&
    data !== null
  ) {
    if (
      "detail" in data &&
      typeof data.detail === "string"
    ) {
      return data.detail;
    }

    if (
      "message" in data &&
      typeof data.message === "string"
    ) {
      return data.message;
    }

    if (
      "error" in data &&
      typeof data.error === "string"
    ) {
      return data.error;
    }
  }

  if (typeof data === "string") {
    const trimmed = data.trim();

    if (trimmed.length > 0) {
      return trimmed;
    }
  }

  return null;
}

function getErrorKind(
  status: number,
): ApiErrorKind {
  if (status === 400 || status === 422) {
    return "validation";
  }

  if (status === 401) {
    return "authentication";
  }

  if (status === 403) {
    return "forbidden";
  }

  if (status === 404) {
    return "not_found";
  }

  if (status === 429) {
    return "rate_limit";
  }

  if (status >= 500) {
    return "server";
  }

  return "unknown";
}

function getUserFriendlyMessage(
  status: number,
  serverMessage: string | null,
): string {
  switch (status) {
    case 400:
      return (
        serverMessage ??
        "The request could not be processed."
      );

    case 401:
      return (
        serverMessage ??
        "Your session has expired. Please sign in again."
      );

    case 403:
      return (
        serverMessage ??
        "You do not have permission to perform this action."
      );

    case 404:
      return (
        serverMessage ??
        "The requested resource could not be found."
      );

    case 422:
      return (
        serverMessage ??
        "Some of the submitted information is invalid."
      );

    case 429:
      return (
        serverMessage ??
        "Too many requests. Please wait and try again."
      );

    default:
      if (status >= 500) {
        return "The CyberGuard server is temporarily unavailable. Please try again later.";
      }

      return (
        serverMessage ??
        "The request could not be completed."
      );
  }
}

async function parseResponse(
  response: Response,
): Promise<unknown> {
  const contentType =
    response.headers.get("content-type");

  const isJson =
    contentType?.includes(
      "application/json",
    );

  try {
    if (isJson) {
      return await response.json();
    }

    return await response.text();
  } catch {
    return null;
  }
}

async function fetchWithTimeout(
  url: string,
  options: RequestInit,
  timeoutMs: number,
): Promise<Response> {
  const controller =
    new AbortController();

  const timeoutId = window.setTimeout(
    () => controller.abort(),
    timeoutMs,
  );

  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
    });
  } catch (error) {
    if (
      error instanceof DOMException &&
      error.name === "AbortError"
    ) {
      throw new ApiError(
        "The request timed out. Please try again.",
        408,
        undefined,
        "timeout",
      );
    }

    throw new ApiError(
      "Unable to connect to the CyberGuard server. Check your internet connection and try again.",
      0,
      undefined,
      "network",
    );
  } finally {
    window.clearTimeout(timeoutId);
  }
}

async function refreshAccessToken(): Promise<RefreshResponse> {
  if (refreshPromise) {
    return refreshPromise;
  }

  const refreshToken =
    getStoredRefreshToken();

  if (!refreshToken) {
    throw new ApiError(
      "Your session has expired. Please sign in again.",
      401,
      undefined,
      "authentication",
    );
  }

  if (!API_BASE_URL) {
    throw new ApiError(
      "CyberGuard API is not configured.",
      0,
      undefined,
      "configuration",
    );
  }

  refreshPromise = (async () => {
    const response =
      await fetchWithTimeout(
        `${API_BASE_URL}/auth/refresh`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            refresh_token: refreshToken,
          }),
        },
        DEFAULT_TIMEOUT_MS,
      );

    const data =
      await parseResponse(response);

    if (!response.ok) {
      clearStoredSession();

      throw new ApiError(
        getUserFriendlyMessage(
          response.status,
          getErrorDetail(data),
        ),
        response.status,
        data,
        getErrorKind(
          response.status,
        ),
      );
    }

    if (
      typeof data !== "object" ||
      data === null ||
      !("access_token" in data) ||
      !("refresh_token" in data)
    ) {
      clearStoredSession();

      throw new ApiError(
        "The server returned an invalid session response.",
        502,
        data,
        "server",
      );
    }

    const refreshed =
      data as RefreshResponse;

    storeRefreshedSession(
      refreshed,
    );

    return refreshed;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {},
  retryAfterRefresh = true,
): Promise<T> {
  const {
    token,
    headers,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    ...fetchOptions
  } = options;

  if (!API_BASE_URL) {
    throw new ApiError(
      "CyberGuard API is not configured.",
      0,
      undefined,
      "configuration",
    );
  }

  const requestHeaders =
    new Headers(headers);

  requestHeaders.set(
    "Content-Type",
    "application/json",
  );

  if (token) {
    requestHeaders.set(
      "Authorization",
      `Bearer ${token}`,
    );
  }

  let response: Response;

  try {
    response =
      await fetchWithTimeout(
        `${API_BASE_URL}${endpoint}`,
        {
          ...fetchOptions,
          headers: requestHeaders,
        },
        timeoutMs,
      );
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new ApiError(
      "Unable to connect to the CyberGuard server. Please try again.",
      0,
      undefined,
      "network",
    );
  }

  const data =
    await parseResponse(response);

  if (!response.ok) {
    const isRefreshableRequest =
      retryAfterRefresh &&
      response.status === 401 &&
      endpoint !== "/auth/login" &&
      endpoint !== "/auth/refresh" &&
      endpoint !== "/auth/logout" &&
      Boolean(token);

    if (isRefreshableRequest) {
      try {
        const refreshed =
          await refreshAccessToken();

        return request<T>(
          endpoint,
          {
            ...options,
            token:
              refreshed.access_token,
          },
          false,
        );
      } catch {
        clearStoredSession();
      }
    }

    throw new ApiError(
      getUserFriendlyMessage(
        response.status,
        getErrorDetail(data),
      ),
      response.status,
      data,
      getErrorKind(
        response.status,
      ),
    );
  }

  return data as T;
}

export const api = {
  get<T>(
    endpoint: string,
    token?: string,
  ): Promise<T> {
    return request<T>(
      endpoint,
      {
        method: "GET",
        token,
      },
    );
  },

  post<T>(
    endpoint: string,
    body?: unknown,
    token?: string,
  ): Promise<T> {
    return request<T>(
      endpoint,
      {
        method: "POST",
        token,
        body:
          body !== undefined
            ? JSON.stringify(body)
            : undefined,
      },
    );
  },

  put<T>(
    endpoint: string,
    body?: unknown,
    token?: string,
  ): Promise<T> {
    return request<T>(
      endpoint,
      {
        method: "PUT",
        token,
        body:
          body !== undefined
            ? JSON.stringify(body)
            : undefined,
      },
    );
  },

  delete<T>(
    endpoint: string,
    token?: string,
  ): Promise<T> {
    return request<T>(
      endpoint,
      {
        method: "DELETE",
        token,
      },
    );
  },
};