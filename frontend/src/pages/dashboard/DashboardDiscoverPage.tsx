import { useNavigate } from 'react-router-dom';
import { DashboardDiscoverPanel } from '../../components/DashboardDiscoverPanel';
import DashboardHeader from '../../components/DashboardHeader';
import { useTranslation } from 'react-i18next';

export default function DashboardDiscoverPage() {
  const { t } = useTranslation(['dashboard']);
  const navigate = useNavigate();

  const features = [
    {
      title: t('dashboard:discoverPage.features.livingMemories.title'),
      description: t('dashboard:discoverPage.features.livingMemories.description'),
      icon: (
        <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      ),
      onClick: () => navigate('/dashboard/ai-clone'),
      bgColor: "bg-purple-100",
      textColor: "text-purple-700",
    },
    {
      title: t('dashboard:discoverPage.features.memoryTest.title'),
      description: t('dashboard:discoverPage.features.memoryTest.description'),
      icon: (
        <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      onClick: () => navigate('/dashboard/mmse-test'),
      bgColor: "bg-blue-100",
      textColor: "text-blue-700",
    },
    {
      title: t('dashboard:discoverPage.features.memoryFilms.title'),
      description: t('dashboard:discoverPage.features.memoryFilms.description'),
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="currentColor" viewBox="0 0 16 16">
          <path d="M0 1a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H1a1 1 0 0 1-1-1zm4 0v6h8V1zm8 8H4v6h8zM1 1v2h2V1zm2 3H1v2h2zM1 7v2h2V7zm2 3H1v2h2zm-2 3v2h2v-2zM15 1h-2v2h2zm-2 3v2h2V4zm2 3h-2v2h2zm-2 3v2h2v-2zm2 3h-2v2h2z"/>
        </svg>
      ),
      onClick: () => navigate('/dashboard/memory-film'),
      bgColor: "bg-indigo-100",
      textColor: "text-indigo-700"
    },
    {
      title: t('dashboard:discoverPage.features.scoreAnalysis.title'),
      description: t('dashboard:discoverPage.features.scoreAnalysis.description'),
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8.515 1.019A7 7 0 0 0 8 1V0a8 8 0 0 1 .589.022zm2.004.45a7 7 0 0 0-.985-.299l.219-.976q.576.129 1.126.342zm1.37.71a7 7 0 0 0-.439-.27l.493-.87a8 8 0 0 1 .979.654l-.615.789a7 7 0 0 0-.418-.302zm1.834 1.79a7 7 0 0 0-.653-.796l.724-.69q.406.429.747.91zm.744 1.352a7 7 0 0 0-.214-.468l.893-.45a8 8 0 0 1 .45 1.088l-.95.313a7 7 0 0 0-.179-.483m.53 2.507a7 7 0 0 0-.1-1.025l.985-.17q.1.58.116 1.17zm-.131 1.538q.05-.254.081-.51l.993.123a8 8 0 0 1-.23 1.155l-.964-.267q.069-.247.12-.501m-.952 2.379q.276-.436.486-.908l.914.405q-.24.54-.555 1.038zm-.964 1.205q.183-.183.35-.378l.758.653a8 8 0 0 1-.401.432z"/>
          <path d="M8 1a7 7 0 1 0 4.95 11.95l.707.707A8.001 8.001 0 1 1 8 0z"/>
          <path d="M7.5 3a.5.5 0 0 1 .5.5v5.21l3.248 1.856a.5.5 0 0 1-.496.868l-3.5-2A.5.5 0 0 1 7 9V3.5a.5.5 0 0 1 .5-.5"/>
        </svg>
      ),
      onClick: () => navigate('/dashboard/mmse-history'),
      bgColor: "bg-green-100",
      textColor: "text-green-700",
    },
    {
      title: t('dashboard:discoverPage.features.careCompanion.title'),
      description: t('dashboard:discoverPage.features.careCompanion.description'),
      icon: <img src="/chat.png" alt="Care Companion" className="h-8 w-8" />,
      onClick: () => navigate('/dashboard/chatbot'),
      bgColor: "bg-cyan-100",
      textColor: "text-cyan-700"
    },
    {
      title: t('dashboard:discoverPage.features.emergencyContacts.title'),
      description: t('dashboard:discoverPage.features.emergencyContacts.description'),
      icon: (
        <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      onClick: () => navigate('/dashboard/contacts'),
      bgColor: "bg-orange-100",
      textColor: "text-orange-700"
    },
    {
      title: t('dashboard:discoverPage.features.memoryMap.title'),
      description: t('dashboard:discoverPage.features.memoryMap.description'),
      icon: (
        <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      onClick: () => navigate('/dashboard/memory-map'),
      bgColor: "bg-red-100",
      textColor: "text-red-700"
    },
    {
      title: t('dashboard:discoverPage.features.miniGames.title'),
      description: t('dashboard:discoverPage.features.miniGames.description'),
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="currentColor" viewBox="0 0 16 16">
          <path d="M10 2a2 2 0 0 1-1.5 1.937v5.087c.863.083 1.5.377 1.5.726 0 .414-.895.75-2 .75s-2-.336-2-.75c0-.35.637-.643 1.5-.726V3.937A2 2 0 1 1 10 2"/>
          <path d="M0 9.665v1.717a1 1 0 0 0 .553.894l6.553 3.277a2 2 0 0 0 1.788 0l6.553-3.277a1 1 0 0 0 .553-.894V9.665c0-.1-.06-.19-.152-.23L9.5 6.715v.993l5.227 2.178a.125.125 0 0 1 .001.23l-5.94 2.546a2 2 0 0 1-1.576 0l-5.94-2.546a.125.125 0 0 1 .001-.23L6.5 7.708l-.013-.988L.152 9.435a.25.25 0 0 0-.152.23"/>
        </svg>
      ),
      onClick: () => navigate('/dashboard/mini-games'),
      bgColor: "bg-pink-100",
      textColor: "text-pink-700"
    }
  ];

  return (
    <div className="lg:col-span-10">
      <DashboardHeader 
        title={t('dashboard:discoverPage.title')}
        description={t('dashboard:discoverPage.description')}
      />
      <DashboardDiscoverPanel features={features} />
    </div>
  );
}
