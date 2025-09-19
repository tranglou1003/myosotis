import React from 'react';
import { ChatMessages } from '../features/chatbot/components/ChatMessages';
import { ChatInput } from '../features/chatbot/components/ChatInput';

interface DashboardChatPanelProps {
  currentMessages: any[];
  handleQuickMessage: (message: string) => void;
}

export const DashboardChatPanel: React.FC<DashboardChatPanelProps> = ({ currentMessages, handleQuickMessage }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-100">
    <div className="h-[730px] flex flex-col">
      <div className="flex-1 flex flex-col min-h-0">
        {currentMessages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-6">
            <div className="w-12 h-12 overflow-hidden mb-4">
              <img src="/chatbot.png" alt="AI Assistant" className="w-full h-full object-cover" />
            </div>
            <h4 className="text-lg font-medium text-gray-900 mb-2">Hi! How can I help?</h4>
            <p className="text-gray-600 text-center mb-6 text-sm">Ask me anything about your health, medications, or wellness</p>
            <div className="grid grid-cols-1 gap-3 w-full max-w-sm">
              <button
                onClick={() => handleQuickMessage("Can you tell me about my medications and any important reminders?")}
                className="text-left p-4 bg-[#5A6DD0]/5 hover:bg-[#5A6DD0]/10 border border-[#5A6DD0]/20 rounded-xl transition-colors group"
              >
                <div className="text-18px text-[#5A6DD0] font-medium group-hover:text-[#5A6DD0]/80 ">Ask about medications</div>
              </button>
              <button
                onClick={() => handleQuickMessage("Can you suggest some memory exercises or activities for brain health?")}
                className="text-left p-4 bg-[#5A6DD0]/5 hover:bg-[#5A6DD0]/10 border border-[#5A6DD0]/20 rounded-xl transition-colors group"
              >
                <div className="text-18px text-[#5A6DD0] font-medium group-hover:text-[#5A6DD0]/80">Memory exercises</div>
              </button>
              <button
                onClick={() => handleQuickMessage("What are some daily health tips for someone with Alzheimer's?")}
                className="text-left p-4 bg-[#5A6DD0]/5 hover:bg-[#5A6DD0]/10 border border-[#5A6DD0]/20 rounded-xl transition-colors group"
              >
                <div className="text-18px text-[#5A6DD0] font-medium group-hover:text-[#5A6DD0]/80">Health tips</div>
              </button>
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-4">
            <ChatMessages />
          </div>
        )}
        <div className="border-t border-gray-100 p-4">
          <ChatInput />
        </div>
      </div>
    </div>
  </div>
);
