import { useAICloneStore } from '../store';
import ProgressStepper from './ProgressStepper';
import Step1Character from './Step1Character';
import Step2Script from './Step2Script';
import Step3Preview from './Step3Preview';

export default function AICloneWizard() {
  const { currentStep } = useAICloneStore();

  return (
    <div className="p-6">
      <ProgressStepper currentStep={currentStep} />

      <div className="mt-8">
        {currentStep === 1 && <Step1Character />}
        {currentStep === 2 && <Step2Script />}
        {currentStep === 3 && <Step3Preview />}
      </div>
    </div>
  );
}
