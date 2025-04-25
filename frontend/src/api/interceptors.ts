import { useAuthStore } from "../auth/authStore";
import { privateApi } from "./axios";

let isRefreshing = false;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let failedQueue: any[] = [];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((p) => {
    if (token) {
      p.resolve(token);
    } else {
      p.reject(error);
    }
  });
  failedQueue = [];
};

export const setupAuthInterceptor = () => {
  const {
    accessToken,
    refreshToken,
    login: setTokens,
    logout: clearTokens,
  } = useAuthStore.getState();

  privateApi.interceptors.request.use((config) => {
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  });

  privateApi.interceptors.response.use(
    (res) => res,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise((resolve) => {
            failedQueue.push({
              resolve: (token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(privateApi(originalRequest));
              },
            });
          });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const response = await privateApi.post("/auth/refresh", {
            refresh_token: refreshToken,
          });

          const newAccess = response.data.access_token;
          const newRefresh = response.data.refresh_token;
          const expiresIn = response.data.expires_in;
          setTokens(newAccess, newRefresh, expiresIn);

          processQueue(null, newAccess);
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
          return privateApi(originalRequest);
        } catch (refreshError) {
          clearTokens();
          window.location.href = "/login";
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      return Promise.reject(error);
    }
  );
};
