import React from 'react';

interface Feature {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: () => void;
  bgColor: string;
  textColor: string;
}

interface DashboardDiscoverPanelProps {
  features: Feature[];
}

export const DashboardDiscoverPanel: React.FC<DashboardDiscoverPanelProps> = ({ features }) => {
  const handleFeatureClick = (feature: Feature) => {
    feature.onClick();
  };

  return (
    <div className="p-4 lg:p-6 mb-4 lg:mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <div
            key={index}
            onClick={() => handleFeatureClick(feature)}
            className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-all cursor-pointer group"
          >
            <div className={`h-12 w-12 rounded-xl ${feature.bgColor} ${feature.textColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
              {feature.icon}
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
            <p className="text-lg text-gray-600 mb-4">{feature.description}</p>
            <div className="flex items-center text-cyan-600 font-medium group-hover:text-cyan-700">
              <span>Open</span>
              <svg className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
