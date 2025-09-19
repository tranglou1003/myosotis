import { useNavigate } from 'react-router-dom';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-cyan-50 antialiased text-[18px] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-semibold text-gray-900">
            Forgot Password
          </h2>
          <p className="mt-2 text-lg text-gray-600">
            Password recovery feature coming soon
          </p>
        </div>
        
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="space-y-6">
            <div className="text-center">
              <div className="h-12 w-12 mx-auto mb-4 bg-cyan-100 text-cyan-700 rounded-xl flex items-center justify-center">
                <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Feature in Development
              </h3>
              <p className="text-lg text-gray-600">
                We're building the password recovery feature. 
                Please contact support if you need assistance.
              </p>
            </div>
            
            <div className="flex flex-col space-y-3">
              <button
                onClick={() => navigate('/login')}
                className="min-h-12 px-5 rounded-xl bg-cyan-600 text-white text-lg font-semibold hover:bg-cyan-700 focus:outline-none focus:ring-4 focus:ring-cyan-300 transition-colors w-full"
              >
                Back to Sign In
              </button>
              
              <button
                onClick={() => navigate('/register')}
                className="min-h-12 px-5 rounded-xl bg-white border border-gray-300 text-gray-700 text-lg hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-gray-200 transition-colors w-full"
              >
                Create New Account
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
