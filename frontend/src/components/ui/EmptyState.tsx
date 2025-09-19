import React from 'react';

interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  actionVariant?: 'primary' | 'secondary';
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionText,
  onAction,
  actionVariant = 'primary',
}) => {
  const buttonClasses = actionVariant === 'primary'
    ? 'min-h-12 px-6 py-2 bg-cyan-600 text-white text-lg font-medium rounded-xl hover:bg-cyan-700 transition-all focus:outline-none focus:ring-4 focus:ring-cyan-300'
    : 'min-h-12 px-6 py-2 text-lg font-medium text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-xl transition-all focus:outline-none focus:ring-4 focus:ring-gray-300';

  return (
    <div className="text-center py-12">
      <div className="w-16 h-16 bg-gray-100 text-gray-400 rounded-full flex items-center justify-center mx-auto mb-6">
        {icon}
      </div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-4">{title}</h2>
      <p className="text-lg text-gray-600 mb-6 max-w-md mx-auto">
        {description}
      </p>
      {actionText && onAction && (
        <button onClick={onAction} className={buttonClasses}>
          {actionText}
        </button>
      )}
    </div>
  );
};
