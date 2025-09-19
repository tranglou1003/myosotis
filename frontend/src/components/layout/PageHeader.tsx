import React from 'react';
import { useNavigate } from 'react-router-dom';

interface PageHeaderProps {
  title?: string;
  showBackButton?: boolean;
  backTo?: string;
  backText?: string;
  rightActions?: React.ReactNode;
  logoClickable?: boolean;
  variant?: 'default' | 'solid';
  useHistory?: boolean;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title = 'Myosotis',
  showBackButton = false,
  backTo = '/dashboard',
  backText = 'Back',
  rightActions,
  logoClickable = true,
  variant = 'default',
  useHistory = true,
}) => {
  const navigate = useNavigate();

  const handleBackClick = () => {
    if (useHistory) {
      navigate(-1);
    } else {
      navigate(backTo);
    }
  };

  const handleLogoClick = () => {
    if (logoClickable) {
      navigate('/dashboard');
    }
  };

  const headerClasses = variant === 'solid' 
    ? "bg-white border-b border-gray-200 shadow-sm"
    : "bg-white/90 backdrop-blur-sm border-b border-gray-200 shadow-sm";

  return (
    <header className={headerClasses}>
      <div className="max-w-5xl mx-auto px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            {showBackButton && (
              <button
                onClick={handleBackClick}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label={backText}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="w-8 h-8" viewBox="0 0 16 16">
                  <path fillRule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8"/>
                </svg>
              </button>
            )}
            
            <div 
              className={`flex items-center gap-3 ${logoClickable ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}`}
              onClick={handleLogoClick}
            >
              <div className="w-8 h-8 rounded-full flex items-center justify-center">
                <img 
                  src="/favicon-32x32.png" 
                  alt="Myosotis Logo" 
                  className="w-8 h-8"
                />
              </div>
              <div className="text-xl font-semibold text-gray-900">
                {title}
              </div>
            </div>
          </div>
          
          {rightActions && (
            <div className="flex items-center space-x-4">
              {rightActions}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export const HeaderButton: React.FC<{
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'memory-add' | 'memory-manage' | 'mmse-test';
  children: React.ReactNode;
}> = ({ onClick, variant = 'secondary', children }) => {
  let baseClasses = "";
  let variantClasses = "";
  
  switch (variant) {
    case 'primary':
      baseClasses = "min-h-12 px-6 py-2 text-lg font-medium rounded-xl transition-all focus:outline-none focus:ring-4";
      variantClasses = "text-cyan-600 hover:text-cyan-700 hover:bg-cyan-50 focus:ring-cyan-300";
      break;
    case 'memory-add':
      baseClasses = "min-h-10 px-4 py-2 text-lg font-medium rounded-lg transition-all focus:outline-none focus:ring-2";
      variantClasses = "bg-cyan-600 text-white hover:bg-cyan-700 focus:ring-cyan-500";
      break;
    case 'memory-manage':
      baseClasses = "min-h-10 px-4 py-2 text-lg font-medium rounded-lg transition-all focus:outline-none focus:ring-2";
      variantClasses = "bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500";
      break;
    case 'mmse-test':
      baseClasses = "px-4 py-2 rounded-lg font-medium transition-colors";
      variantClasses = "bg-cyan-600 text-white hover:bg-cyan-700";
      break;
    case 'secondary':
    default:
      baseClasses = "min-h-12 px-6 py-2 text-lg font-medium rounded-xl transition-all focus:outline-none focus:ring-4";
      variantClasses = "text-gray-600 hover:text-gray-700 hover:bg-gray-50 focus:ring-gray-300";
      break;
  }

  return (
    <button
      onClick={onClick}
      className={`${baseClasses} ${variantClasses}`}
    >
      {children}
    </button>
  );
};
