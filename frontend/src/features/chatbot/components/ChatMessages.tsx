import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { useChatbotStore } from '../store';
import { LoadingSpinner } from '../../../components';
import { chatMarkdownComponents } from '../utils/markdownComponents';
import { useTranslation } from 'react-i18next';

export const ChatMessages: React.FC = () => {
  const { t } = useTranslation('chatbot');
  const { currentMessages, isLoading, isSending } = useChatbotStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentMessages, isSending, t]);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <LoadingSpinner text={t('messages.loading')} />
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-8">
      {currentMessages.map((message) => (
        <div key={message.id} className="space-y-6">
          <div className="flex justify-end">
            <div className="max-w-[75%]">
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-3xl rounded-br-lg px-6 py-4 shadow-lg">
                <p className="text-lg leading-relaxed">
                  {message.user_message}
                </p>
              </div>
            </div>
          </div>

          {/* Bot Response */}
          {message.bot_response && (
            <div className="flex justify-start">
              <div className="max-w-[75%]">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <img src="/chatbot.png" alt={t('messages.careCompanion')} className="w-6 h-6" />
                  </div>
                  
                  <div className="flex-1">
                    {message.bot_response.split('\n\n').filter(paragraph => paragraph.trim()).map((paragraph, idx) => (
                      <div key={idx} className={`bg-white/90 backdrop-blur-sm text-gray-900 rounded-3xl rounded-bl-lg px-6 py-4 shadow-lg border border-gray-200/50 ${idx > 0 ? 'mt-3' : ''}`}>
                        <div className="text-lg leading-relaxed prose max-w-none prose-headings:text-gray-900 prose-p:text-gray-800 prose-strong:text-gray-900">
                          <ReactMarkdown components={chatMarkdownComponents}>
                            {paragraph}
                          </ReactMarkdown>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}

      {/* Typing Indicator */}
      {isSending && (
        <div className="flex justify-start">
          <div className="max-w-[75%]">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                <img src="/chatbot.png" alt={t('messages.careCompanion')} className="w-6 h-6" />
              </div>
              
              <div className="bg-white/90 backdrop-blur-sm text-gray-900 rounded-3xl rounded-bl-lg px-6 py-4 shadow-lg border border-gray-200/50">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};
