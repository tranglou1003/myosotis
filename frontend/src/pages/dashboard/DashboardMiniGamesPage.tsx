import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import DashboardHeader from '../../components/DashboardHeader';

export default function DashboardMiniGamesPage() {
  const navigate = useNavigate();
  const { t } = useTranslation('miniGames');

  const games = [
    {
      id: 'sudoku',
      title: t('games.sudoku.title'),
      description: t('games.sudoku.description'),
      icon: (
        <svg className="h-16 w-16 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 10h18M3 14h18m-9-4v8m-7 0V7a2 2 0 012-2h14a2 2 0 012 2v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
        </svg>
      ),
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      buttonColor: 'bg-blue-600 hover:bg-blue-700',
      buttonText: t('games.sudoku.playButton'),
      onClick: () => navigate('/dashboard/mini-games/sudoku')
    },
    {
      id: 'picture-recall',
      title: t('games.pictureRecall.title'),
      description: t('games.pictureRecall.description'),
      icon: (
        <svg className="h-16 w-16 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-800',
      buttonColor: 'bg-purple-600 hover:bg-purple-700',
      buttonText: t('games.pictureRecall.playButton'),
      onClick: () => navigate('/dashboard/mini-games/picture-recall')
    }
  ];

  return (
    <div className="lg:col-span-10">
      <DashboardHeader 
        title={t('title')} 
        description={t('description')}
      />
      
      <div className="bg-gray-50 min-h-screen p-6">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {games.map((game) => (
              <div
                key={game.id}
                className={`${game.bgColor} ${game.borderColor} border-2 rounded-2xl p-8 transition-all duration-300 hover:shadow-lg hover:scale-105`}
              >
                <div className="text-center">
                  <div className="flex justify-center mb-6">
                    {game.icon}
                  </div>
                  
                  <h3 className={`text-2xl font-bold ${game.textColor} mb-4`}>
                    {game.title}
                  </h3>
                  
                  <p className="text-gray-600 text-lg mb-8 leading-relaxed">
                    {game.description}
                  </p>
                  
                  <button
                    onClick={game.onClick}
                    className={`${game.buttonColor} text-white px-8 py-4 rounded-xl font-semibold text-lg transition-colors duration-200 shadow-md hover:shadow-lg`}
                  >
                    {game.buttonText}
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-12 text-center">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h4 className="text-lg font-semibold text-gray-800 mb-2">
                {t('benefits.title')}
              </h4>
              <p className="text-gray-600">
                {t('benefits.description')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
