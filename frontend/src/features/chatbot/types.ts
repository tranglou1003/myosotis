
export interface ChatMessage {
  id: number;
  user_message: string;
  bot_response: string;
  created_at: string;
}

export interface ChatSessionSummary {
  session_id: string;
  session_number: number;
  session_name: string;
  total_messages: number;
  last_message_preview: string;
  created_at: string;
  last_active: string;
}

export interface ChatSessionDetails {
  session_id: string;
  user_id: number;
  session_number: number;
  session_name: string;
  total_messages: number;
  messages: ChatMessage[];
  created_at: string;
  last_active: string;
}

export interface SendMessagePayload {
  user_id: number;
  message: string;
  session_number?: number;
}

export interface SendMessageResponse {
  session_id: string;
  response: string;
  timestamp: string;
}

export interface ConversationStarter {
  id: string;
  text: string;
  icon: React.ReactNode;
}


export interface ChatbotState {
  
  activeSession: ChatSessionSummary | null;
  currentMessages: ChatMessage[];
  
  
  sessionHistory: ChatSessionSummary[];
  
  
  isLoading: boolean;
  isSending: boolean;
  isHistoryLoading: boolean;
  error: string | null;
  
  
  isChatOpen: boolean;
  inputMessage: string;
}

export interface ChatbotActions {
  
  setActiveSession: (session: ChatSessionSummary | null) => void;
  createNewSession: () => void;
  getNextSessionNumber: (userId: number) => Promise<number>;
  
  
  sendMessage: (payload: SendMessagePayload) => Promise<void>;
  setInputMessage: (message: string) => void;
  
  
  loadSessionHistory: (userId: number, limit?: number, offset?: number) => Promise<void>;
  loadSessionDetails: (userId: number, sessionId: string, limit?: number, offset?: number) => Promise<void>;
  deleteSession: (sessionId: string) => Promise<void>;
  
  
  toggleChat: () => void;
  openChat: () => void;
  closeChat: () => void;
  clearError: () => void;
  
  
  clearUserData: () => void;
  reset: () => void;
}

export type ChatbotStore = ChatbotState & ChatbotActions;
