import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { getRegisterSchema, type RegisterFormData } from "./validation";
import { useAuthStore } from "./store";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export default function RegisterForm() {
  const { t } = useTranslation(['auth']);
  const navigate = useNavigate();
  const { register: registerUser, isLoading, error, clearError } = useAuthStore();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { 
    register, 
    handleSubmit, 
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(getRegisterSchema(t)),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setSubmitError(null);
      clearError();
      await registerUser(data);
      navigate('/dashboard/account?edit=true');
    } catch (error) {
      console.error('Registration failed:', error);
      setSubmitError(t('auth:register.registrationFailed'));
    }
  };

  const displayError = error || submitError;

  return (
    <div className="w-full max-w-md mx-auto">
      <button
        type="button"
        onClick={() => navigate('/')}
        className="mb-6 flex items-center gap-2 text-lg text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:ring-4 focus:ring-cyan-300 rounded-lg p-2"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        {t('auth:register.backToHome')}
      </button>

      <div className="mb-8 text-center">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
          {t('auth:register.title')}
        </h2>
        <p className="text-lg text-gray-600">
          {t('auth:register.subtitle')}
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label htmlFor="email" className="block text-lg font-medium text-gray-900 mb-2">
            {t('auth:register.emailLabel')} <span className="text-red-500">{t('auth:register.required')}</span>
          </label>
          <input
            id="email"
            type="email"
            {...register("email")}
            placeholder={t('auth:register.emailPlaceholder')}
            className="min-h-12 w-full px-4 py-3 text-lg border border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-cyan-300 focus:border-cyan-600"
            aria-invalid={errors.email ? 'true' : 'false'}
            aria-describedby={errors.email ? 'email-error' : 'email-help'}
          />
          <p id="email-help" className="text-lg text-gray-600 mt-1">
            {t('auth:register.emailHelp')}
          </p>
          {errors.email && (
            <span id="email-error" className="block text-lg text-red-600 mt-1" role="alert">
              {errors.email.message}
            </span>
          )}
        </div>

        <div>
          <label htmlFor="full_name" className="block text-lg font-medium text-gray-900 mb-2">
            {t('auth:register.fullNameLabel')} <span className="text-red-500">{t('auth:register.required')}</span>
          </label>
          <input
            id="full_name"
            type="text"
            {...register("profile.full_name")}
            placeholder={t('auth:register.fullNamePlaceholder')}
            className="min-h-12 w-full px-4 py-3 text-lg border border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-cyan-300 focus:border-cyan-600"
            aria-invalid={errors.profile?.full_name ? 'true' : 'false'}
            aria-describedby={errors.profile?.full_name ? 'full_name-error' : undefined}
          />
          {errors.profile?.full_name && (
            <span id="full_name-error" className="block text-lg text-red-600 mt-1" role="alert">
              {errors.profile.full_name.message}
            </span>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-lg font-medium text-gray-900 mb-2">
            {t('auth:register.passwordLabel')} <span className="text-red-500">{t('auth:register.required')}</span>
          </label>
          <input
            id="password"
            type="password"
            {...register("password")}
            placeholder={t('auth:register.passwordPlaceholder')}
            className="min-h-12 w-full px-4 py-3 text-lg border border-gray-300 rounded-xl focus:outline-none focus:ring-4 focus:ring-cyan-300 focus:border-cyan-600"
            aria-invalid={errors.password ? 'true' : 'false'}
            aria-describedby={errors.password ? 'password-error' : 'password-help'}
          />
          {errors.password && (
            <span id="password-error" className="block text-lg text-red-600 mt-1" role="alert">
              {errors.password.message}
            </span>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting || isLoading}
          className="min-h-12 w-full px-5 rounded-xl bg-cyan-600 text-white text-lg font-semibold hover:bg-cyan-700 focus:outline-none focus:ring-4 focus:ring-cyan-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting || isLoading ? (
            <span className="flex items-center justify-center gap-3">
              <svg className="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {t('auth:register.submittingButton')}
            </span>
          ) : (
            t('auth:register.submitButton')
          )}
        </button>

        {displayError && (
          <div className="bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl text-lg font-medium" role="alert">
            {displayError}
          </div>
        )}

        <div className="text-center text-lg text-gray-600">
          {t('auth:register.haveAccount')}{' '}
          <button 
            type="button"
            onClick={() => navigate('/login')}
            className="text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:ring-4 focus:ring-cyan-300 rounded-lg p-1"
          >
            {t('auth:register.signInNow')}
          </button>
        </div>

        <div className="text-center text-sm text-gray-500 mt-4">
          <p>{t('auth:register.profileNote')}</p>
        </div>
      </form>
    </div>
  );
}
