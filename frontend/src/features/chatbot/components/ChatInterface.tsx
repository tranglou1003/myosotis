import React, { useEffect } from 'react';
import { useChatbotStore } from '../store';
import { useAuthStore } from '../../auth/store';
import { ChatSessionHistory } from './ChatSessionHistory';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { ConversationStarters } from './ConversationStarters';
import { useTranslation } from 'react-i18next';

export const ChatInterface: React.FC = () => {
  const { t } = useTranslation('chatbot');
  const { user } = useAuthStore();
  const { 
    isChatOpen, 
    currentMessages,
    activeSession,
    closeChat,
    loadSessionHistory,
  } = useChatbotStore();
  
  useEffect(() => {
    if (isChatOpen && user?.id) {
      loadSessionHistory(user.id);
    }
  }, [isChatOpen, user?.id, loadSessionHistory, t]);

  if (!isChatOpen) {
    return null;
  }

  const showConversationStarters = currentMessages.length === 0;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="w-full max-w-7xl h-full max-h-[90vh] bg-white rounded-2xl shadow-2xl flex overflow-hidden">
        <div className="w-[30%] bg-gray-50 border-r border-gray-200 flex flex-col">
          <ChatSessionHistory />
        </div>

        <div className="w-[70%] flex flex-col">
          <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-white">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 overflow-hidden">
                <img src="/chatbot.png" alt={t('messages.careCompanion')} className="w-full h-full object-cover" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  { activeSession?.session_name || t('interface.newConversation')}
                </h1>
                <p className="text-sm text-gray-500">
                  {t('interface.intelligentAssistant')}
                </p>
              </div>
            </div>
            
            <button
              onClick={closeChat}
              className="w-10 h-10 flex items-center justify-center rounded-full 
                       text-gray-500 hover:text-gray-700 hover:bg-gray-100
                       transition-colors duration-200 focus:outline-none 
                       focus:ring-2 focus:ring-gray-300"
              aria-label={t('interface.closeChat')}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="flex-1 flex flex-col min-h-0">
            {showConversationStarters ? (
              <ConversationStarters />
            ) : (
              <>
                <ChatMessages />
                <ChatInput />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
