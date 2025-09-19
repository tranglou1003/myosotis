import { useTranslation } from 'react-i18next';

interface GenerationNotificationModalProps {
  isOpen: boolean;
  onGoToGallery: () => void;
  onWaitOnPage: () => void;
}

export default function GenerationNotificationModal({
  isOpen,
  onGoToGallery,
  onWaitOnPage,
}: GenerationNotificationModalProps) {
  const { t } = useTranslation(['aiClone']);
  
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl p-8 max-w-md mx-4">
        <div className="text-center">
          {/* Icon */}
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>

          {/* Headline */}
          <h2 className="text-2xl font-bold text-gray-900 mb-4">{t('aiClone:modal.title')}</h2>

          {/* Body Text */}
          <p className="text-gray-600 mb-8">
            {t('aiClone:modal.description')}
          </p>

          {/* Action Buttons */}
          <div className="space-y-3">
            {/* Primary Button */}
            <button
              onClick={onGoToGallery}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              {t('aiClone:modal.buttons.checkHistoryLater')}
            </button>

            {/* Secondary Button */}
            <button
              onClick={onWaitOnPage}
              className="w-full bg-gray-100 text-gray-700 py-3 px-6 rounded-lg font-medium hover:bg-gray-200 transition-colors"
            >
              {t('aiClone:modal.buttons.stayOnPage')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
