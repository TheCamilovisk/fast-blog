import axios from "axios";
import { Settings } from "../config";

const baseURL = Settings.API_URL;

export const publicApi = axios.create({
  baseURL: baseURL,
});

export const privateApi = axios.create({
  baseURL: baseURL,
});
