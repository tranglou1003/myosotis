import React from 'react';

interface LoadingSpinnerProps {
  text?: string;
  size?: 'sm' | 'md' | 'lg';
  centered?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  text = 'Loading...',
  size = 'md',
  centered = true,
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  const containerClasses = centered 
    ? 'flex items-center justify-center py-8'
    : 'flex items-center gap-3';

  return (
    <div className={containerClasses}>
      <div className={`animate-spin rounded-full border-b-2 border-cyan-600 ${sizeClasses[size]}`}></div>
      {text && <span className="ml-3 text-gray-600">{text}</span>}
    </div>
  );
};
