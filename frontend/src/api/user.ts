import axios from "axios";
import type { UserApiResponse, EmergencyContact, EmergencyContactPayload, UserUpdatePayload } from "../types/user";

const userAPI = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

userAPI.interceptors.response.use(
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

export function getUserInfo(userId: number): Promise<UserApiResponse> {
  return userAPI.get<UserApiResponse>(`/api/v1/users/${userId}`)
    .then(res => res.data);
}

export function updateUserInfo(userId: number, payload: Partial<UserUpdatePayload>): Promise<UserApiResponse> {
  console.log('Updating user info with payload:', payload);
  return userAPI.put(`/api/v1/users/${userId}`, payload)
    .then(res => {
      console.log('Update response:', res.data);
      return res.data;
    })
    .catch(err => {
      console.error('Update error:', err.response?.data || err.message);
      throw err;
    });
}

export function getEmergencyContacts(userId: number): Promise<{ data: EmergencyContact[] }> {
  return userAPI.get(`/api/v1/emergency-contacts/user/${userId}`)
    .then(res => res.data);
}

export function createEmergencyContact(userId: number, payload: EmergencyContactPayload): Promise<{ data: EmergencyContact }> {
  return userAPI.post(`/api/v1/emergency-contacts/user/${userId}`, payload)
    .then(res => res.data);
}

export function updateEmergencyContact(contactId: number, payload: EmergencyContactPayload): Promise<{ data: EmergencyContact }> {
  return userAPI.put(`/api/v1/emergency-contacts/${contactId}`, payload)
    .then(res => res.data);
}

export function deleteEmergencyContact(contactId: number): Promise<void> {
  return userAPI.delete(`/api/v1/emergency-contacts/${contactId}`)
    .then(() => void 0);
}
