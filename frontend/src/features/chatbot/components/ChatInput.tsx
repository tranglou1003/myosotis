import React, { useState } from 'react';
import { useChatbotStore } from '../store';
import { useAuthStore } from '../../auth/store';
import { useTranslation } from 'react-i18next';

export const ChatInput: React.FC = () => {
  const { t } = useTranslation('chatbot');
  const { user } = useAuthStore();
  const { 
    isSending, 
    activeSession,
    sendMessage, 
  } = useChatbotStore();

  const [localMessage, setLocalMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!user?.id || !localMessage.trim() || isSending) return;
    
    const messageToSend = localMessage.trim();
    setLocalMessage(''); 
    
    await sendMessage({
      user_id: user.id,
      message: messageToSend,
      session_number: activeSession?.session_number,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const form = e.currentTarget.closest('form');
      if (form) {
        form.requestSubmit();
      }
    }
  };

  return (
    <div className="border-t border-gray-200/50 bg-white/80 backdrop-blur-sm p-6">
      <form onSubmit={handleSubmit} className="flex gap-4 items-end max-w-4xl mx-auto">
        <div className="flex-1">
          <textarea
            value={localMessage}
            onChange={(e) => setLocalMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={t('input.placeholder')}
            disabled={isSending}
            rows={1}
            className="w-full px-6 py-4 text-lg border border-gray-300/50 rounded-3xl 
                       focus:outline-none focus:ring-2 focus:ring-blue-500/20 
                       focus:border-blue-400 resize-none min-h-[56px] max-h-32
                       disabled:opacity-50 disabled:cursor-not-allowed
                       bg-white/90 backdrop-blur-sm shadow-sm
                       placeholder:text-gray-500"
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: '#3b82f6 #f1f5f9'
            }}
          />
        </div>
        
        <button
          type="submit"
          disabled={!localMessage.trim() || isSending}
          className="flex-shrink-0 w-14 h-14 bg-gradient-to-r from-blue-500 to-indigo-600
                     hover:from-blue-600 hover:to-indigo-700 text-white rounded-2xl 
                     flex items-center justify-center transition-all duration-200 
                     focus:outline-none focus:ring-2 focus:ring-blue-500/20
                     disabled:opacity-50 disabled:cursor-not-allowed 
                     disabled:hover:from-blue-500 disabled:hover:to-indigo-600
                     shadow-lg hover:shadow-xl hover:scale-105"
          aria-label={t('input.sendMessage')}
        >
          {isSending ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </form>
    </div>
  );
};
