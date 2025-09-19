import React, { useEffect, useState } from 'react';
import { useChatbotStore } from '../store';
import { useAuthStore } from '../../auth/store';
import { LoadingSpinner } from '../../../components';
import { useTranslation } from 'react-i18next';

export const ChatSessionHistory: React.FC = () => {
  const { t } = useTranslation('chatbot');
  const { user } = useAuthStore();
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);
  const { 
    sessionHistory, 
    activeSession, 
    isHistoryLoading,
    isLoading,
    error,
    loadSessionHistory,
    loadSessionDetails,
    createNewSession,
    setActiveSession,
    deleteSession,
    clearError,
  } = useChatbotStore();

  useEffect(() => {
    if (user?.id && sessionHistory.length === 0) {
      loadSessionHistory(user.id);
    }
  }, [user?.id, sessionHistory.length, loadSessionHistory, t]);

  // const formatDate = (dateString: string) => {
  //   const date = new Date(dateString);
  //   const now = new Date();
  //   const isToday = date.toDateString() === now.toDateString();
    
  //   if (isToday) {
  //     return `${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} Today`;
  //   }
    
  //   const yesterday = new Date(now);
  //   yesterday.setDate(yesterday.getDate() - 1);
  //   const isYesterday = date.toDateString() === yesterday.toDateString();
    
  //   if (isYesterday) {
  //     return `${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} Yesterday`;
  //   }
    
  //   return date.toLocaleDateString([], { 
  //     month: 'short', 
  //     day: 'numeric',
  //     hour: '2-digit', 
  //     minute: '2-digit' 
  //   });
  // };

  const handleSessionSelect = async (session: typeof sessionHistory[0]) => {
    if (!user?.id) return;
    
    setActiveSession(session);
    await loadSessionDetails(user.id, session.session_id);
  };

  const handleNewChat = () => {
    createNewSession();
  };

  const handleDeleteClick = (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation(); 
    setSessionToDelete(sessionId);
  };

  const confirmDelete = async () => {
    if (sessionToDelete) {
      await deleteSession(sessionToDelete);
      setSessionToDelete(null);
    }
  };

  const cancelDelete = () => {
    setSessionToDelete(null);
  };

  if (isHistoryLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <LoadingSpinner text={t('conversations.loading')} />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-3 sm:p-4 border-b border-gray-200">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3 sm:mb-4">{t('conversations.title')}</h2>
        <button
          onClick={handleNewChat}
          className="w-full bg-[#5A6DD0] hover:bg-[#1932b1] text-white py-2.5 sm:py-3 px-3 sm:px-4 
                     rounded-lg font-medium text-sm sm:text-lg transition-colors duration-200 
                     flex items-center justify-center gap-2 focus:outline-none 
                     focus:ring-2 focus:ring-[#92d7e7]/50"
        >
          <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          {t('conversations.newChat')}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border-l-4 border-red-400">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
              <button
                onClick={clearError}
                className="mt-2 text-sm text-red-600 underline hover:text-red-500"
              >
                {t('errors.dismiss')}
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {sessionHistory.length === 0 ? (
          <div className="p-4 sm:p-6 text-center text-gray-500">
            <svg className="w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p className="text-base sm:text-lg">{t('conversations.noConversations')}</p>
            <p className="text-xs sm:text-sm mt-1">{t('conversations.startNewChat')}</p>
          </div>
        ) : (
          <div className="p-1.5 sm:p-2">
            {sessionHistory.map((session) => (
              <div
                key={session.session_id}
                className={`relative mb-1.5 sm:mb-2 rounded-lg transition-colors duration-200
                  ${activeSession?.session_id === session.session_id 
                    ? 'bg-gray-100 border-2 border-gray-300' 
                    : 'bg-white hover:bg-gray-50 border border-gray-200'
                  }`}
              >
                <button
                  onClick={() => handleSessionSelect(session)}
                  className="w-full text-left p-3 sm:p-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#92d7e7]/50"
                >
                  <div className="flex flex-col gap-1.5 sm:gap-2 pr-8 sm:pr-10">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900 text-sm sm:text-lg leading-tight">
                        {session.session_name}
                      </h3>
                    </div>
                    <p className="text-gray-600 text-xs sm:text-base line-clamp-2 leading-relaxed font-normal">
                      {session.last_message_preview}
                    </p>
                    <div className="text-xs sm:text-sm text-gray-500">
                      <span>{t('conversations.messageCount', { count: session.total_messages })}</span>
                    </div>
                  </div>
                </button>
                
                <button
                  onClick={(e) => handleDeleteClick(session.session_id, e)}
                  className="absolute top-1.5 sm:top-2 right-1.5 sm:right-2 p-1.5 sm:p-2 text-gray-400 hover:text-red-500 
                           hover:bg-red-50 rounded-lg transition-colors duration-200
                           focus:outline-none focus:ring-2 focus:ring-red-200"
                  title={t('conversations.deleteConversation')}
                >
                  <svg className="w-5 h-5 sm:w-8 sm:h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {sessionToDelete && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl shadow-xl w-full max-w-md">
            <div className="p-8">
              <div className="flex items-center justify-center w-16 h-16 mx-auto mb-6 bg-red-100 rounded-full">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </div>

              <div className="text-center mb-8">
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                  {t('deleteDialog.title')}
                </h3>
                <p className="text-lg text-gray-600">
                  {t('deleteDialog.message')}
                </p>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={cancelDelete}
                  disabled={isLoading}
                  className="flex-1 min-h-12 px-6 py-2 text-lg font-medium text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-xl transition-all focus:outline-none focus:ring-4 focus:ring-gray-300 border border-gray-200 disabled:opacity-50"
                >
                  {t('deleteDialog.cancel')}
                </button>
                <button
                  onClick={confirmDelete}
                  disabled={isLoading}
                  className="flex-1 min-h-12 px-6 py-2 bg-red-600 text-white text-lg font-medium rounded-xl hover:bg-red-700 transition-all focus:outline-none focus:ring-4 focus:ring-red-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    t('deleteDialog.delete')
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
