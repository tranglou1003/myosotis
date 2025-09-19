import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { AICloneWizard, useAICloneStore } from '../features/ai-clone';
import { ProtectedRoute } from '../features/auth';
import GenerationNotificationModal from '../features/ai-clone/components/GenerationNotificationModal';
import { useTranslation } from 'react-i18next';

export default function AICloneCreatePage() {
  const { t } = useTranslation(['aiClone']);
  const navigate = useNavigate();
  const { reset, isGenerating } = useAICloneStore();
  const [showGenerationModal, setShowGenerationModal] = useState(false);

  useEffect(() => {
    reset();
  }, [reset]);

  useEffect(() => {
    if (isGenerating) {
      setShowGenerationModal(true);
    }
  }, [isGenerating]);

  const handleGoToGallery = () => {
    setShowGenerationModal(false);
    navigate('/dashboard/ai-clone?tab=history');
  };

  const handleWaitOnPage = () => {
    setShowGenerationModal(false);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-cyan-50">
        <div className="w-full h-full p-6">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <button
                  onClick={() => navigate(-1)}
                  className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-800 hover:bg-white rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  {t('aiClone:navigation.back')}
                </button>
                <button
                  onClick={() => navigate('/dashboard/ai-clone?tab=history')}
                  className="flex items-center gap-2 px-4 py-2 text-cyan-600 hover:text-cyan-700 hover:bg-white rounded-lg transition-colors font-medium"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {t('aiClone:navigation.viewGallery')}
                </button>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('aiClone:createPage.title')}</h1>
              <p className="text-gray-600">{t('aiClone:createPage.description')}</p>
            </div>

            {/* AI Clone Wizard Container */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <AICloneWizard />
            </div>
          </div>
        </div>
        
        <GenerationNotificationModal
          isOpen={showGenerationModal}
          onGoToGallery={handleGoToGallery}
          onWaitOnPage={handleWaitOnPage}
        />
      </div>
    </ProtectedRoute>
  );
}
