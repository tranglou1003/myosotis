import { useAuthStore } from '../../features/auth';
import { EmergencyContactsPanel } from '../../components/EmergencyContactsPanel';
import DashboardHeader from '../../components/DashboardHeader';
import { useTranslation } from 'react-i18next';
export default function DashboardContactsPage() {
  const { user } = useAuthStore();
  const { t } = useTranslation(['dashboard']);  
  return (
    <div className="lg:col-span-10">
      <DashboardHeader 
        title={t('dashboard:emergencyContacts.title')} 
        description={t('dashboard:emergencyContacts.description')}
      />
      <div className="bg-white rounded-lg shadow p-6">
        <EmergencyContactsPanel userId={user?.id} />
      </div>
    </div>
  );
}
