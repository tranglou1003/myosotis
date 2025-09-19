import type { WizardStep } from '../types';
import { useTranslation } from 'react-i18next';

interface ProgressStepperProps {
  currentStep: WizardStep;
}

export default function ProgressStepper({ currentStep }: ProgressStepperProps) {
  const { t } = useTranslation(['aiClone']);
  
  const steps = [
    { number: 1, title: t('aiClone:wizard.steps.character') },
    { number: 2, title: t('aiClone:wizard.steps.script') },
    { number: 3, title: t('aiClone:wizard.steps.preview') },
  ];

  return (
    <div className="w-full max-w-3xl mx-auto mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.number} className="flex items-center">
            <div
              className={`
                w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold
                ${
                  step.number <= currentStep
                    ? 'bg-cyan-600 text-white'
                    : 'bg-gray-200 text-gray-500'
                }
              `}
            >
              {step.number}
            </div>
            
            <span
              className={`
                ml-3 text-sm font-medium
                ${
                  step.number <= currentStep
                    ? 'text-cyan-600'
                    : 'text-gray-500'
                }
              `}
            >
              {step.title}
            </span>
            
            {index < steps.length - 1 && (
              <div
                className={`
                  flex-1 h-0.5 mx-6 min-w-[80px]
                  ${
                    step.number < currentStep
                      ? 'bg-cyan-600'
                      : 'bg-gray-200'
                  }
                `}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
