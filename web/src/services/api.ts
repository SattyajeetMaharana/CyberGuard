const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  console.warn("VITE_API_BASE_URL is not configured.");
}

export class ApiError extends Error {
  status: number;
  data?: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

interface RequestOptions extends RequestInit {
  token?: string;
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { token, headers, ...fetchOptions } = options;

  const requestHeaders = new Headers(headers);

  requestHeaders.set("Content-Type", "application/json");

  if (token) {
    requestHeaders.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers: requestHeaders,
  });

  const contentType = response.headers.get("content-type");
  const isJson = contentType?.includes("application/json");

  const data = isJson
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    throw new ApiError(
      typeof data === "object" &&
        data !== null &&
        "detail" in data
        ? String(data.detail)
        : "API request failed.",
      response.status,
      data,
    );
  }

  return data as T;
}

export const api = {
  get<T>(endpoint: string, token?: string): Promise<T> {
    return request<T>(endpoint, {
      method: "GET",
      token,
    });
  },

  post<T>(
    endpoint: string,
    body?: unknown,
    token?: string,
  ): Promise<T> {
    return request<T>(endpoint, {
      method: "POST",
      token,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(
    endpoint: string,
    body?: unknown,
    token?: string,
  ): Promise<T> {
    return request<T>(endpoint, {
      method: "PUT",
      token,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(endpoint: string, token?: string): Promise<T> {
    return request<T>(endpoint, {
      method: "DELETE",
      token,
    });
  },
};