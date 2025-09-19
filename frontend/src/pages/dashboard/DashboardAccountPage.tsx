import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../../features/auth/store';
import { getUserInfo, updateUserInfo } from '../../api/user';
import type { UserData } from '../../types/user';
import { DashboardAccountPanel } from '../../components/DashboardAccountPanel';
import DashboardHeader from '../../components/DashboardHeader';
import { useTranslation } from 'react-i18next';

export default function DashboardAccountPage() {
  const { t } = useTranslation(['dashboard']);
  const { user, updateUser } = useAuthStore();
  const [searchParams, setSearchParams] = useSearchParams();

  const [userData, setUserData] = useState<UserData | null>(null);
  const [isLoadingUserData, setIsLoadingUserData] = useState(false);
  const [userDataError, setUserDataError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    dateOfBirth: '',
    gender: '',
    address: '',
    city: '',
    hometown: '',
    country: '',
    medicalNotes: ''
  });

  const fetchUserData = useCallback(async () => {
    if (!user?.id) {
      setUserDataError(t('dashboard:accountPage.errors.userIdNotFound'));
      setIsLoadingUserData(false);
      return;
    }

    try {
      setIsLoadingUserData(true);
      const response = await getUserInfo(user.id);
      setUserData(response.data);

      setFormData({
        fullName: response.data.profile?.full_name || '',
        email: response.data.email || '',
        phone: response.data.phone || '',
        dateOfBirth: response.data.profile?.date_of_birth || '',
        gender: response.data.profile?.gender || '',
        address: response.data.profile?.address || '',
        city: response.data.profile?.city || '',
        hometown: response.data.profile?.hometown || '',
        country: response.data.profile?.country || '',
        medicalNotes: ''
      });
      setUserDataError(null);
    } catch (err) {
      setUserDataError(err instanceof Error ? err.message : t('dashboard:accountPage.errors.fetchFailed'));
    } finally {
      setIsLoadingUserData(false);
    }
  }, [user?.id, t]);

  useEffect(() => {
    fetchUserData();
  }, [fetchUserData]);

  
  useEffect(() => {
    const editParam = searchParams.get('edit');
    if (editParam === 'true') {
      setIsEditing(true);
      
      setSearchParams(prev => {
        const newParams = new URLSearchParams(prev);
        newParams.delete('edit');
        return newParams;
      });
    }
  }, [searchParams, setSearchParams]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async () => {
    if (!user?.id) return;

    setIsSaving(true);
    setUserDataError(null);
    setSuccessMessage(null);

    try {
      const payload = {
        phone: formData.phone,
        email: formData.email,
        profile: {
          full_name: formData.fullName,
          date_of_birth: formData.dateOfBirth,
          gender: formData.gender,
          address: formData.address,
          city: formData.city,
          hometown: formData.hometown,
          country: formData.country,
        }
      };

      await updateUserInfo(user.id, payload);

      const freshUserData = await getUserInfo(user.id);
      setUserData(freshUserData.data);

      const updatedUser = {
        ...user,
        email: freshUserData.data.email,
        phone: freshUserData.data.phone,
        profile: {
          ...user.profile,
          id: freshUserData.data.profile?.id || user.profile?.id || user.id,
          user_id: user.id,
          full_name: freshUserData.data.profile?.full_name || '',
          date_of_birth: freshUserData.data.profile?.date_of_birth,
          gender: freshUserData.data.profile?.gender as 'male' | 'female' | undefined,
          phone: freshUserData.data.profile?.phone,
          address: freshUserData.data.profile?.address,
          city: freshUserData.data.profile?.city,
          hometown: freshUserData.data.profile?.hometown,
          country: freshUserData.data.profile?.country,
          avatar_url: freshUserData.data.profile?.avatar_url,
          created_at: user.profile?.created_at || new Date().toISOString(),
        }
      };
      updateUser(updatedUser);

      setIsEditing(false);
      setSuccessMessage(t('dashboard:accountPage.messages.updateSuccess'));
    } catch (err) {
      setUserDataError(err instanceof Error ? err.message : t('dashboard:accountPage.errors.saveFailed'));
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    if (userData) {
      setFormData({
        fullName: userData.profile?.full_name || '',
        email: userData.email || '',
        phone: userData.phone || '',
        dateOfBirth: userData.profile?.date_of_birth || '',
        gender: userData.profile?.gender || '',
        address: userData.profile?.address || '',
        city: userData.profile?.city || '',
        hometown: userData.profile?.hometown || '',
        country: userData.profile?.country || '',
        medicalNotes: ''
      });
    }
    setIsEditing(false);
  };

  return (
    <div className="lg:col-span-10">
      <DashboardHeader 
        title={t('dashboard:accountPage.title')}
        description={t('dashboard:accountPage.description')}
      />
      <DashboardAccountPanel
        isLoadingUserData={isLoadingUserData}
        isEditing={isEditing}
        isSaving={isSaving}
        userDataError={userDataError}
        successMessage={successMessage}
        formData={formData}
        handleInputChange={handleInputChange}
        handleSave={handleSave}
        handleCancel={handleCancel}
        setIsEditing={setIsEditing}
      />
    </div>
  );
}
