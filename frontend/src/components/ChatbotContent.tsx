import { useEffect, useState } from 'react';
import { useChatbotStore } from '../features/chatbot/store';
import { ChatSessionHistory } from '../features/chatbot/components/ChatSessionHistory';
import { ChatMessages } from '../features/chatbot/components/ChatMessages';
import { ChatInput } from '../features/chatbot/components/ChatInput';
import { ConversationStarters } from '../features/chatbot/components/ConversationStarters';
import { useAuthStore } from '../features/auth/store';
import { useTranslation } from 'react-i18next';

export default function ChatbotContent() {
  const { t } = useTranslation('chatbot');
  const { user } = useAuthStore();
  const { 
    currentMessages,
    loadSessionHistory,
    clearUserData,
  } = useChatbotStore();
  
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  useEffect(() => {
    if (user?.id) {
      clearUserData();
      loadSessionHistory(user.id);
    } else {
      clearUserData();
    }
  }, [user?.id, loadSessionHistory, clearUserData, t]);

  const showConversationStarters = currentMessages.length === 0;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="h-[700px] lg:h-[800px] flex">
          <div className={`${isSidebarOpen ? 'block' : 'hidden'} lg:block w-80 border-r border-gray-200 bg-gray-50/50`}>
            <div className="bg-white">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setIsSidebarOpen(false)}
                  className="lg:hidden p-1 rounded-md hover:bg-gray-100"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="overflow-y-auto h-full">
              <ChatSessionHistory />
            </div>
          </div>

          <div className="flex-1 flex flex-col">
            <div className="flex-shrink-0 bg-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto">
              {showConversationStarters ? (
                <div className="h-full p-6 flex flex-col justify-center">
                  <ConversationStarters />
                </div>
              ) : (
                <div className="h-full">
                  <ChatMessages />
                </div>
              )}
            </div>
            <div className="flex-shrink-0 p-4 border-t border-gray-200 bg-white">
              <ChatInput />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
