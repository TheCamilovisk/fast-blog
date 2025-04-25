import { create } from "zustand";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  expiresAt: number | null;
  login: (access: string, refresh: string, expiresIn: number) => void;
  logout: () => void;
  checkTokenValidity: () => boolean;
};

const getExpirationTime = (expiresIn: number) => Date.now() + expiresIn * 1000;

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem("access_token"),
  refreshToken: localStorage.getItem("refresh_token"),
  expiresAt: Number(localStorage.getItem("expires_at")),

  login: (access: string, refresh: string, expiresIn: number) => {
    const expiresAt = getExpirationTime(expiresIn);
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
    localStorage.setItem("expires_at", String(expiresAt));
    set({ accessToken: access, refreshToken: refresh, expiresAt });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("expires_at");
    set({
      accessToken: null,
      refreshToken: null,
      expiresAt: null,
    });
  },

  checkTokenValidity: () => {
    const expiresAt = parseInt(localStorage.getItem("expires_at") || "0", 10);
    return expiresAt > Date.now();
  },
}));
