import axios from "axios";
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

  try {
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
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail);
    } else {
      throw error;
    }
  }
};

export const refreshAccessToken = async (
  refreshToken: string
): Promise<{
  accessToken: string;
  expiresIn: number;
}> => {
  try {
    const res = await publicApi.post("/auth/refresh", {
      refresh_token: refreshToken,
    });

    return {
      accessToken: res.data.access_token,
      expiresIn: res.data.expires_in,
    };
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail);
    } else {
      throw error;
    }
  }
};
