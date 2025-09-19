import { useState, useEffect } from 'react';
import { DashboardInfoPanel } from '../../components/DashboardInfoPanel';
import DashboardHeader from '../../components/DashboardHeader';
import { useNavigate } from 'react-router-dom';
import Lottie from 'lottie-react';
import { useTranslation } from 'react-i18next';

export default function DashboardHomePage() {
  const { t } = useTranslation(['dashboard']);
  const navigate = useNavigate();
  const [currentCarouselIndex, setCurrentCarouselIndex] = useState(0);
  const [isCarouselPaused, setIsCarouselPaused] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(true);
  const [animationData, setAnimationData] = useState(null);

  const dashboardFeatures = [
    {
      title: t('dashboard:homePage.features.livingMemories.title'),
      subtitle: t('dashboard:homePage.features.livingMemories.subtitle'),
      icon: <img src="/living-memories.png" alt="Living Memories" className="h-12 w-12" />,
      onClick: () => navigate('/dashboard/ai-clone')
    },
    {
      title: t('dashboard:homePage.features.memoryTest.title'),
      subtitle: t('dashboard:homePage.features.memoryTest.subtitle'),
      icon: <img src="/test-icon.png" alt="Memory Test" className="h-12 w-12" />,
      onClick: () => navigate('/dashboard/mmse-test')
    },
    {
      title: t('dashboard:homePage.features.careCompanion.title'),
      subtitle: t('dashboard:homePage.features.careCompanion.subtitle'),
      icon: <img src="/chat.png" alt="Care Companion" className="h-12 w-12" />,
      onClick: () => navigate('/dashboard/chatbot')
    },
    {
      title: t('dashboard:homePage.features.memoryFilms.title'),
      subtitle: t('dashboard:homePage.features.memoryFilms.subtitle'),
      icon: <img src="/film.png" alt="Memory Films" className="h-12 w-12" />,
      onClick: () => navigate('/dashboard/memory-film')
    },
    {
      title: t('dashboard:homePage.features.memoryMap.title'),
      subtitle: t('dashboard:homePage.features.memoryMap.subtitle'),
      icon: (
        <svg className="h-12 w-12 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      onClick: () => navigate('/dashboard/memory-map')
    },
    {
      title: t('dashboard:homePage.features.miniGames.title'),
      subtitle: t('dashboard:homePage.features.miniGames.subtitle'),
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-black" fill="currentColor" viewBox="0 0 16 16">
          <path d="M10 2a2 2 0 0 1-1.5 1.937v5.087c.863.083 1.5.377 1.5.726 0 .414-.895.75-2 .75s-2-.336-2-.75c0-.35.637-.643 1.5-.726V3.937A2 2 0 1 1 10 2"/>
          <path d="M0 9.665v1.717a1 1 0 0 0 .553.894l6.553 3.277a2 2 0 0 0 1.788 0l6.553-3.277a1 1 0 0 0 .553-.894V9.665c0-.1-.06-.19-.152-.23L9.5 6.715v.993l5.227 2.178a.125.125 0 0 1 .001.23l-5.94 2.546a2 2 0 0 1-1.576 0l-5.94-2.546a.125.125 0 0 1 .001-.23L6.5 7.708l-.013-.988L.152 9.435a.25.25 0 0 0-.152.23"/>
        </svg>
      ),
      onClick: () => navigate('/dashboard/mini-games')
    }
  ];

  const handleCarouselScroll = (direction: 'left' | 'right') => {
    if (direction === 'left') {
      setCurrentCarouselIndex((prev) => {
        if (prev <= 0) {
          return dashboardFeatures.length - 1;
        }
        return prev - 1;
      });
    } else {
      setCurrentCarouselIndex((prev) => {
        if (prev >= dashboardFeatures.length - 1) {
          return 0;
        }
        return prev + 1;
      });
    }
  };

  useEffect(() => {
    if (isCarouselPaused) return;

    const interval = setInterval(() => {
      setCurrentCarouselIndex((prev) => {
        if (prev >= dashboardFeatures.length - 1) {
          return 0;
        }
        return prev + 1;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [isCarouselPaused, dashboardFeatures.length]);

  useEffect(() => {
    if (currentCarouselIndex >= dashboardFeatures.length) {
      setIsTransitioning(false);
      const timer = setTimeout(() => {
        setCurrentCarouselIndex(currentCarouselIndex - dashboardFeatures.length);
        setTimeout(() => setIsTransitioning(true), 50);
      }, 800);
      return () => clearTimeout(timer);
    } else if (currentCarouselIndex < 0) {
      setIsTransitioning(false);
      const timer = setTimeout(() => {
        setCurrentCarouselIndex(currentCarouselIndex + dashboardFeatures.length);
        setTimeout(() => setIsTransitioning(true), 50);
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [currentCarouselIndex, dashboardFeatures.length]);

  useEffect(() => {
    const loadAnimation = async () => {
      try {
        const response = await fetch('/mental-therapy.json');
        const data = await response.json();
        setAnimationData(data);
      } catch (error) {
        console.error('Failed to load animation:', error);
      }
    };

    loadAnimation();
  }, []);

  const handleNavigateToChart = () => {
    navigate('/dashboard/mmse-history');
  };

  const getCurrentDate = () => {
    const now = new Date();
    const months = [
      t('dashboard:homePage.calendar.months.january'),
      t('dashboard:homePage.calendar.months.february'),
      t('dashboard:homePage.calendar.months.march'),
      t('dashboard:homePage.calendar.months.april'),
      t('dashboard:homePage.calendar.months.may'),
      t('dashboard:homePage.calendar.months.june'),
      t('dashboard:homePage.calendar.months.july'),
      t('dashboard:homePage.calendar.months.august'),
      t('dashboard:homePage.calendar.months.september'),
      t('dashboard:homePage.calendar.months.october'),
      t('dashboard:homePage.calendar.months.november'),
      t('dashboard:homePage.calendar.months.december')
    ];
    return {
      month: months[now.getMonth()],
      year: now.getFullYear(),
      day: now.getDate()
    };
  };

  const generateCalendarDays = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();

    let startingDayOfWeek = firstDay.getDay();
    startingDayOfWeek = startingDayOfWeek === 0 ? 6 : startingDayOfWeek - 1;

    const days = [];
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day);
    }

    return days;
  };

  const currentDate = getCurrentDate();
  const calendarDays = generateCalendarDays();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-8">
      <div className="lg:col-span-8">
        <DashboardHeader 
          title={t('dashboard:homePage.title')}
          description={t('dashboard:homePage.description')}
        />
        
        <DashboardInfoPanel
          dashboardFeatures={dashboardFeatures}
          currentCarouselIndex={currentCarouselIndex}
          isTransitioning={isTransitioning}
          setIsCarouselPaused={setIsCarouselPaused}
          handleCarouselScroll={handleCarouselScroll}
          onNavigateToChart={handleNavigateToChart}
        />
      </div>

      <div className="lg:col-span-4">
        <div className="p-4 lg:p-6 mb-4 lg:mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <img src="/calendar.png" alt="Calendar" className="h-5 w-5" />
              <h3 className="text-lg font-semibold">{currentDate.month} {currentDate.year}</h3>
            </div>
            <div className="flex space-x-1">
              <button className="p-1 rounded-md hover:bg-gray-100" aria-label="Previous Month">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button className="p-1 rounded-md hover:bg-gray-100" aria-label="Next Month">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-1 mb-2">
            {[
              t('dashboard:homePage.calendar.daysOfWeekShort.monday'),
              t('dashboard:homePage.calendar.daysOfWeekShort.tuesday'),
              t('dashboard:homePage.calendar.daysOfWeekShort.wednesday'),
              t('dashboard:homePage.calendar.daysOfWeekShort.thursday'),
              t('dashboard:homePage.calendar.daysOfWeekShort.friday'),
              t('dashboard:homePage.calendar.daysOfWeekShort.saturday'),
              t('dashboard:homePage.calendar.daysOfWeekShort.sunday')
            ].map((day, index) => (
              <div key={index} className="text-xs text-[#888888] text-center py-2 font-medium">
                {day}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-1">
            {calendarDays.map((day, index) => (
              <div key={index} className="aspect-square flex items-center justify-center">
                {day && (
                  <button
                    className={`w-8 h-8 rounded-full text-sm hover:bg-gray-100 transition-colors ${
                      day === currentDate.day 
                        ? 'bg-[#5A6DD0] text-white hover:bg-[#5A6DD0]/90' 
                        : 'text-[#333333]'
                    }`}
                  >
                    {day}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="p-4 lg:p-6 text-center">
          <div className="w-40 h-40 sm:w-48 sm:h-48 lg:w-56 lg:h-56 mx-auto mb-4 bg-gradient-to-br from-[#5A6DD0]/10 to-[#5A6DD0]/20 rounded-full flex items-center justify-center">
            {animationData ? (
              <Lottie 
                animationData={animationData}
                loop={true}
                autoplay={true}
                className="w-40 h-40 sm:w-48 sm:h-48 lg:w-56 lg:h-56"
              />
            ) : (
              <div className="w-40 h-40 sm:w-48 sm:h-48 lg:w-56 lg:h-56 bg-[#5A6DD0]/20 rounded-full flex items-center justify-center">
                <div className="w-6 h-6 bg-[#5A6DD0] rounded-full animate-pulse"></div>
              </div>
            )}
          </div>
          <h4 className="font-semibold text-[#333333] mb-2">{t('dashboard:homePage.healthAssistant.title')}</h4>
          <p className="text-[#888888] text-sm">{t('dashboard:homePage.healthAssistant.description')}</p>
        </div>
      </div>
    </div>
  );
}
