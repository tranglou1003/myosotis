
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "./store";
import RegisterForm from "./RegisterForm";

export default function RegisterPage() {
  const { t } = useTranslation('auth');
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  if (isAuthenticated) {
    return null; 
  }

  return (
    <div className="min-h-screen bg-cyan-50 antialiased text-[18px] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-lg w-full">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-semibold text-gray-900">
            {t('register.pageTitle')}
          </h2>
          <p className="mt-2 text-lg text-gray-600">
            {t('register.pageSubtitle')}
          </p>
        </div>
        
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <RegisterForm />
        </div>
        
        <div className="text-center text-lg text-gray-500 mt-6">
          {t('register.termsText')}{' '}
          <button className="text-cyan-600 hover:text-cyan-700 font-medium">
            {t('register.termsOfService')}
          </button>{' '}
          {t('register.and')}{' '}
          <button className="text-cyan-600 hover:text-cyan-700 font-medium">
            {t('register.privacyPolicy')}
          </button>.
        </div>
      </div>
    </div>
  );
}
