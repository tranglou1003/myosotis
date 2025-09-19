import React from 'react';
import { SimpleChart } from './SimpleChart';

interface DashboardInfoPanelProps {
  dashboardFeatures: Array<{
    title: string;
    subtitle: string;
    icon: React.ReactNode;
    onClick: () => void;
  }>;
  currentCarouselIndex: number;
  isTransitioning: boolean;
  setIsCarouselPaused: (paused: boolean) => void;
  handleCarouselScroll: (direction: 'left' | 'right') => void;
  onNavigateToChart: () => void;
}

export const DashboardInfoPanel: React.FC<DashboardInfoPanelProps> = ({
  dashboardFeatures,
  currentCarouselIndex,
  isTransitioning,
  setIsCarouselPaused,
  handleCarouselScroll,
  onNavigateToChart,
}) => {
  return (
    <>
      <div
        className="px-4 lg:px-6 mb-4 lg:mb-6"
        onMouseEnter={() => setIsCarouselPaused(true)}
        onMouseLeave={() => setIsCarouselPaused(false)}
      >
        <div className="flex items-center justify-end mb-4">
          <div className="flex space-x-2">
            <button
              onClick={() => handleCarouselScroll('left')}
              className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
              aria-label="Previous"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={() => handleCarouselScroll('right')}
              className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
              aria-label="Next"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <div className="relative overflow-hidden">
          <div
            className={`flex ${isTransitioning ? 'transition-transform duration-[400ms] ease-in-out' : ''}`}
            style={{
              transform: `translateX(-${currentCarouselIndex * (100/3)}%)`
            }}
          >
            {[...dashboardFeatures, ...dashboardFeatures].map((feature, index) => {
              const originalIndex = index % dashboardFeatures.length;
              const isActive = originalIndex === (currentCarouselIndex % dashboardFeatures.length);

              return (
                <div
                  key={index}
                  className="flex-shrink-0 w-1/3 px-2"
                >
                  <div
                    onClick={feature.onClick}
                    className={`w-full border rounded-[16px] p-6 cursor-pointer hover:shadow-lg transition-all transform hover:scale-105 ${
                      isActive
                        ? 'bg-gradient-to-br from-[#5A6DD0] to-[#5A6DD0]/80 text-white border-[#5A6DD0]'
                        : 'bg-white border-gray-100 text-gray-900'
                    }`}
                  >
                    <div className={`w-16 h-16 rounded-[12px] flex items-center justify-center mb-4 ${
                      isActive
                        ? 'bg-white/20'
                        : 'bg-gray-50'
                    }`}>
                      {feature.icon}
                    </div>
                    <h4 className={`font-semibold mb-2 text-lg ${
                      isActive ? 'text-white' : 'text-[#333333]'
                    }`}>
                      {feature.title}
                    </h4>
                    <p className={`text-sm ${
                      isActive ? 'text-white/80' : 'text-[#888888]'
                    }`}>
                      {feature.subtitle}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="px-4 lg:px-6 mb-4 lg:mb-6">
        <SimpleChart onNavigateToChart={onNavigateToChart} />
      </div>
    </>
  );
};
