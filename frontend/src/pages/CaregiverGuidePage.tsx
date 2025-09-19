
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../components/layout';

export default function CaregiverGuidePage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-cyan-50 antialiased text-[18px]">
      <PageHeader 
        title="Caregiver Guide"
        showBackButton={true}
        backTo="/"
        backText="Back to Home"
      />
      
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-12">
          <div className="w-24 h-24 mx-auto mb-6 bg-cyan-100 rounded-full flex items-center justify-center">
            <svg className="w-12 h-12 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h1 className="text-4xl md:text-5xl font-semibold text-gray-900 mb-4">
            Caregiver Guide
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            How to register and use Myosotis to support people with Alzheimer's
          </p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 space-y-8">
          
          <div className="border-l-4 border-cyan-600 pl-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-12 w-12 bg-cyan-100 text-cyan-700 rounded-xl flex items-center justify-center text-lg font-semibold">1</div>
              <h2 className="text-2xl font-semibold text-gray-900">Prepare Information</h2>
            </div>
            <div className="space-y-4 text-lg text-gray-700">
              <p>Before registering, please prepare the following information:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Your email (caregiver) or patient's email</li>
                <li>Patient's full name</li>
                <li>Contact phone number</li>
                <li>Patient's date of birth (if available)</li>
                <li>Home address</li>
                <li>Emergency contact information</li>
              </ul>
            </div>
          </div>

          <div className="border-l-4 border-cyan-600 pl-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-12 w-12 bg-cyan-100 text-cyan-700 rounded-xl flex items-center justify-center text-lg font-semibold">2</div>
              <h2 className="text-2xl font-semibold text-gray-900">Register Account</h2>
            </div>
            <div className="space-y-4 text-lg text-gray-700">
              <p>There are 2 ways to register:</p>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-cyan-50 border-2 border-cyan-200 rounded-xl p-6">
                  <h3 className="text-xl font-semibold text-cyan-800 mb-3"> Caregiver Registration</h3>
                  <p className="text-lg text-cyan-700">
                    You can register an account with your email and fill in the patient's information. 
                    This helps you manage and support them easily.
                  </p>
                </div>
                <div className="bg-cyan-50 border-2 border-cyan-200 rounded-xl p-6">
                  <h3 className="text-xl font-semibold text-cyan-800 mb-3"> Register Together</h3>
                  <p className="text-lg text-cyan-700">
                    If the patient can still participate, sit with them to register. 
                    This helps them feel respected and involved in the care process.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="border-l-4 border-cyan-600 pl-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-12 w-12 bg-cyan-100 text-cyan-700 rounded-xl flex items-center justify-center text-lg font-semibold">3</div>
              <h2 className="text-2xl font-semibold text-gray-900">Set Up System</h2>
            </div>
            <div className="space-y-4 text-lg text-gray-700">
              <p>After successful registration, you can:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Set up medication schedules and reminders</li>
                <li>Create family photo albums to support memory</li>
                <li>Record important medical information</li>
                <li>Invite other family members to join</li>
                <li>Connect with healthcare professionals</li>
              </ul>
            </div>
          </div>

          <div className="bg-cyan-50 border-2 border-cyan-200 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <svg className="w-8 h-8 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h3 className="text-xl font-semibold text-cyan-800"> Helpful Tips</h3>
            </div>
            <ul className="space-y-3 text-lg text-cyan-700">
              <li className="flex items-start gap-3">
                <span>Take time to get familiar with the system gradually. No need to rush.</span>
              </li>
              <li className="flex items-start gap-3">
                <span>Listen to the patient's opinions about features they want to use.</span>
              </li>
              <li className="flex items-start gap-3">
                <span>Don't hesitate to contact us if you need additional support.</span>
              </li>
              <li className="flex items-start gap-3">
                <span>Information can be updated and edited at any time.</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 text-center space-y-6">
          <button
            onClick={() => navigate('/register')}
            className="min-h-12 px-8 rounded-xl bg-cyan-600 text-white text-lg font-semibold hover:bg-cyan-700 focus:outline-none focus:ring-4 focus:ring-cyan-300 transition-colors w-full max-w-md mx-auto block"
          >
            Start Registration Now
          </button>
          
          <div className="text-center">
            <p className="text-lg text-gray-600 mb-4">
              Need additional support?
            </p>
            <div className="space-y-2">
              <button className="block mx-auto text-lg font-medium text-cyan-600 hover:text-cyan-700 underline focus:outline-none focus:ring-4 focus:ring-cyan-300 rounded-lg p-2">
                Call support hotline: 1900-xxxx
              </button>
              <button className="block mx-auto text-lg font-medium text-cyan-600 hover:text-cyan-700 underline focus:outline-none focus:ring-4 focus:ring-cyan-300 rounded-lg p-2">
                Email: support@myosotis.com
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
