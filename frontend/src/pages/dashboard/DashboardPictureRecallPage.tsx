import { useTranslation } from 'react-i18next';
import { PictureRecallGame } from '../../features/picture-recall';
import DashboardHeader from '../../components/DashboardHeader';

export default function DashboardPictureRecallPage() {
  const { t } = useTranslation('miniGames');

  return (
    <div className="lg:col-span-10">
      <DashboardHeader 
        title={t('pages.pictureRecall.title')} 
        description={t('pages.pictureRecall.description')}
      />
      
      <PictureRecallGame />
    </div>
  );
}
