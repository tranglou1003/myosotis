import axios from "axios";
import type { 
  SendMessagePayload,
  SendMessageResponse,
  ChatSessionSummary,
  ChatSessionDetails
} from "./types";

const chatAPI = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

chatAPI.interceptors.response.use(
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

export function sendChatMessage(payload: SendMessagePayload): Promise<SendMessageResponse> {
  return chatAPI.post<SendMessageResponse>('/api/v1/chat/', payload)
    .then(res => res.data);
}

export function getChatSessionHistory(
  userId: number, 
  limit: number = 20, 
  offset: number = 0
): Promise<ChatSessionSummary[]> {
  return chatAPI.get<ChatSessionSummary[]>(`/api/v1/chat/history/${userId}`, {
    params: { limit, offset }
  }).then(res => res.data);
}

export function getChatSessionDetails(
  userId: number, 
  sessionId: string, 
  limit: number = 50, 
  offset: number = 0
): Promise<ChatSessionDetails> {
  return chatAPI.get<ChatSessionDetails>(`/api/v1/chat/history/${userId}/${sessionId}`, {
    params: { limit, offset }
  }).then(res => res.data);
}

export function getLatestSession(userId: number): Promise<ChatSessionDetails> {
  return chatAPI.get<ChatSessionDetails>(`/api/v1/chat/latest-session/${userId}`)
    .then(res => res.data);
}

export function deleteChatSession(sessionId: string): Promise<void> {
  return chatAPI.delete(`/api/v1/chat/session/${sessionId}`)
    .then(() => void 0);
}
