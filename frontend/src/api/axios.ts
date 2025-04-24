import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL;

export const publicApi = axios.create({
  baseURL: baseURL,
});

export const privateApi = axios.create({
  baseURL: baseURL,
});
