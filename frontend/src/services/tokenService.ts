import { publicApi } from "../api/axios";

export const getTokens = async (
  identifier: string,
  password: string
): Promise<{
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}> => {
  const form = new URLSearchParams();
  form.append("username", identifier);
  form.append("password", password);

  const res = await publicApi.post("/auth/token", form, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return {
    accessToken: res.data.access_token,
    refreshToken: res.data.refresh_token,
    expiresIn: res.data.expires_in,
  };
};

export const refreshAccessToken = async (
  refreshToken: string
): Promise<{
  accessToken: string;
  expiresIn: number;
}> => {
  const res = await publicApi.post("/auth/refresh", {
    refresh_token: refreshToken,
  });

  return {
    accessToken: res.data.access_token,
    expiresIn: res.data.expires_in,
  };
};
