import axios from "axios";
import type { RegisterPayload, LoginPayload, ApiResponse, LoginResponseData, RegisterResponseData } from "./types";

const authAPI = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});


authAPI.interceptors.response.use(
  (response) => {
    if (response.data.success === false) {
      throw new Error(response.data.message || 'API request failed');
    }
    return response;
  },
  (error) => {
    if (error.response?.data?.message) {
      throw new Error(error.response.data.message);
    }
    throw error;
  }
);

export function loginUser(payload: LoginPayload): Promise<LoginResponseData> {
  return authAPI.post<ApiResponse<LoginResponseData>>("/api/auth/login", payload)
    .then(res => res.data.data);
}

export function registerUser(payload: RegisterPayload): Promise<RegisterResponseData> {
  return authAPI.post<ApiResponse<RegisterResponseData>>("/api/auth/register", payload)
    .then(res => res.data.data);
}

export function logoutUser(): Promise<void> {
  return Promise.resolve();
}
