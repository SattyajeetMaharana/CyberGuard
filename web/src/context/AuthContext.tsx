import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { api } from "../services/api";
import {
  clearSession as clearStoredSession,
  getAccessToken,
  getRefreshToken,
  setSession,
} from "../services/authStorage";
import type { User } from "../types";

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

interface AuthContextValue {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<
  AuthContextValue | undefined
>(undefined);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);

  const [accessToken, setAccessToken] =
    useState<string | null>(getAccessToken());

  const [refreshToken, setRefreshToken] =
    useState<string | null>(getRefreshToken());

  const [isLoading, setIsLoading] = useState(true);

  const clearSession = useCallback(() => {
    clearStoredSession();

    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const response =
        await api.post<AuthResponse>(
          "/auth/login",
          {
            email,
            password,
          },
        );

      setSession(
        response.access_token,
        response.refresh_token,
      );

      setAccessToken(response.access_token);
      setRefreshToken(response.refresh_token);
      setUser(response.user);
    },
    [],
  );

  const logout = useCallback(async () => {
    const currentRefreshToken =
      getRefreshToken();

    try {
      if (currentRefreshToken) {
        await api.post(
          "/auth/logout",
          {
            refresh_token:
              currentRefreshToken,
          },
        );
      }
    } finally {
      clearSession();
    }
  }, [clearSession]);

  useEffect(() => {
    let cancelled = false;

    async function restoreSession() {
      const storedAccessToken =
        getAccessToken();

      if (!storedAccessToken) {
        if (!cancelled) {
          setIsLoading(false);
        }

        return;
      }

      try {
        const currentUser =
          await api.get<User>(
            "/users/me",
            storedAccessToken,
          );

        if (!cancelled) {
          setUser(currentUser);

          setAccessToken(
            getAccessToken(),
          );

          setRefreshToken(
            getRefreshToken(),
          );
        }
      } catch {
        if (!cancelled) {
          clearSession();
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void restoreSession();

    return () => {
      cancelled = true;
    };
  }, [clearSession]);

  const value =
    useMemo<AuthContextValue>(
      () => ({
        user,
        accessToken,
        refreshToken,
        isAuthenticated:
          Boolean(user && accessToken),
        isLoading,
        login,
        logout,
      }),
      [
        user,
        accessToken,
        refreshToken,
        isLoading,
        login,
        logout,
      ],
    );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside an AuthProvider.",
    );
  }
  return context;
}