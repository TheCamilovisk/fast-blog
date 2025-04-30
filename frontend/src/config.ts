const env = import.meta.env;

export const Settings: {
  API_URL: string;
  APP_URL: string;
} = {
  API_URL: env.VITE_API_URL,
  APP_URL: env.VITE_APP_URL,
};
