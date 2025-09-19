import React from 'react';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick: () => void;
  iconBgColor?: string;
  iconTextColor?: string;
  showArrow?: boolean;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  onClick,
  iconBgColor = 'bg-cyan-100',
  iconTextColor = 'text-cyan-700',
  showArrow = false,
}) => {
  return (
    <div 
      onClick={onClick}
      className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-all cursor-pointer group"
    >
      <div className={`h-12 w-12 rounded-xl ${iconBgColor} ${iconTextColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-lg text-gray-600">{description}</p>
      {showArrow && (
        <div className="mt-4 flex items-center text-cyan-600 font-medium group-hover:text-cyan-700">
          <span>Open</span>
          <svg className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      )}
    </div>
  );
};
