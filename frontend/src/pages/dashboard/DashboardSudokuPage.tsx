import { useTranslation } from 'react-i18next';
import { SudokuGame } from '../../features/sudoku/SudokuGame';
import DashboardHeader from '../../components/DashboardHeader';

export default function DashboardSudokuGamePage() {
  const { t } = useTranslation('miniGames');

  return (
    <div className="lg:col-span-10">
      <DashboardHeader 
        title={t('pages.sudoku.title')} 
        description={t('pages.sudoku.description')}
      />
      
      <div className="bg-gray-50 min-h-screen">
        <SudokuGame />
      </div>
    </div>
  );
}
