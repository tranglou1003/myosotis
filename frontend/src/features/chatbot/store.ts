import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { ChatbotStore } from './types';
import { sendChatMessage, getChatSessionHistory, getChatSessionDetails, getLatestSession, deleteChatSession } from './api';

const initialState = {
  
  activeSession: null,
  currentMessages: [],
  
  
  sessionHistory: [],
  
  
  isLoading: false,
  isSending: false,
  isHistoryLoading: false,
  error: null,
  
  
  isChatOpen: false,
  inputMessage: '',
};

export const useChatbotStore = create<ChatbotStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      
      setActiveSession: (session) => {
        set({ activeSession: session, currentMessages: [] });
      },

      createNewSession: () => {
        set({ 
          activeSession: null, 
          currentMessages: [],
          inputMessage: '',
        });
      },

      getNextSessionNumber: async (userId) => {
        try {
          const latestSession = await getLatestSession(userId);
          return latestSession.session_number + 1;
        } catch (error) {
          
          if (error instanceof Error && error.message.includes('404')) {
            return 1;
          }
          
          try {
            const sessions = await getChatSessionHistory(userId, 1, 0);
            if (sessions.length > 0) {
              return Math.max(...sessions.map(s => s.session_number)) + 1;
            }
            return 1;
          } catch {
            return 1;
          }
        }
      },

      
      sendMessage: async (payload) => {
        const state = get();
        
        if (state.isSending) return;
        if (!payload.message.trim()) return;
        
        set({ isSending: true, error: null });
        
        
        const userMessage = {
          id: Date.now(), 
          user_message: payload.message,
          bot_response: '', 
          created_at: new Date().toISOString(),
        };

        set(state => ({ 
          currentMessages: [...state.currentMessages, userMessage],
          inputMessage: '', 
        }));
        
        try {
          
          let sessionNumber = payload.session_number;
          if (!sessionNumber && !state.activeSession) {
            sessionNumber = await get().getNextSessionNumber(payload.user_id);
          } else if (state.activeSession) {
            sessionNumber = state.activeSession.session_number;
          }

          const messagePayload = {
            ...payload,
            session_number: sessionNumber,
          };

          const response = await sendChatMessage(messagePayload);
          
          
          const newActiveSession = state.activeSession || {
            session_id: response.session_id,
            session_number: sessionNumber || parseInt(response.session_id), 
            session_name: `${sessionNumber || response.session_id}`,
            total_messages: 1,
            last_message_preview: payload.message,
            created_at: response.timestamp,
            last_active: response.timestamp,
          };
          
          set(state => ({
            currentMessages: state.currentMessages.map(msg => 
              msg.id === userMessage.id 
                ? { ...msg, bot_response: response.response }
                : msg
            ),
            activeSession: newActiveSession,
            
            sessionHistory: state.activeSession 
              ? state.sessionHistory.map(session => 
                  session.session_id === newActiveSession.session_id
                    ? { ...session, total_messages: session.total_messages + 1, last_message_preview: payload.message, last_active: response.timestamp }
                    : session
                )
              : [newActiveSession, ...state.sessionHistory]
          }));
          
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
          set({ error: errorMessage });
          
          
          set(state => ({
            currentMessages: state.currentMessages.filter(msg => msg.id !== userMessage.id)
          }));
        } finally {
          set({ isSending: false });
        }
      },

      setInputMessage: (message) => {
        set({ inputMessage: message });
      },

      
      loadSessionHistory: async (userId, limit = 20, offset = 0) => {
        set({ isHistoryLoading: true, error: null });
        
        try {
          const sessions = await getChatSessionHistory(userId, limit, offset);
          set({ sessionHistory: sessions });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to load session history';
          set({ error: errorMessage, sessionHistory: [] });
        } finally {
          set({ isHistoryLoading: false });
        }
      },

      loadSessionDetails: async (userId, sessionId, limit = 50, offset = 0) => {
        set({ isLoading: true, error: null });
        
        try {
          const sessionDetails = await getChatSessionDetails(userId, sessionId, limit, offset);
          
          
          const activeSession = get().sessionHistory.find(s => s.session_id === sessionId);
          
          set({ 
            currentMessages: sessionDetails.messages,
            activeSession: activeSession || {
              session_id: sessionDetails.session_id,
              session_number: sessionDetails.session_number,
              session_name: sessionDetails.session_name,
              total_messages: sessionDetails.total_messages,
              last_message_preview: sessionDetails.messages[0]?.user_message || '',
              created_at: sessionDetails.created_at,
              last_active: sessionDetails.last_active,
            }
          });
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to load session details';
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      deleteSession: async (sessionId) => {
        set({ isLoading: true, error: null });
        
        try {
          await deleteChatSession(sessionId);
          
          
          set(state => ({
            sessionHistory: state.sessionHistory.filter(session => session.session_id !== sessionId),
            
            activeSession: state.activeSession?.session_id === sessionId ? null : state.activeSession,
            
            currentMessages: state.activeSession?.session_id === sessionId ? [] : state.currentMessages,
          }));
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Failed to delete session';
          set({ error: errorMessage });
        } finally {
          set({ isLoading: false });
        }
      },

      
      toggleChat: () => {
        set(state => ({ isChatOpen: !state.isChatOpen }));
      },

      openChat: () => {
        set({ isChatOpen: true });
      },

      closeChat: () => {
        set({ isChatOpen: false });
      },

      clearError: () => {
        set({ error: null });
      },

      clearUserData: () => {
        set({
          activeSession: null,
          currentMessages: [],
          sessionHistory: [],
          inputMessage: '',
          error: null,
        });
      },

      reset: () => {
        set(initialState);
      },
    }),
    { name: 'chatbot-store' }
  )
);
