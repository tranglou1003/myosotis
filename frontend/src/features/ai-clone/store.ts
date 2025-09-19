import { create } from 'zustand';
import type { WizardStepData, WizardStep } from './types';

interface AICloneStore extends WizardStepData {
  currentStep: WizardStep;
  
  
  setCurrentStep: (step: WizardStep) => void;
  updateData: (data: Partial<WizardStepData>) => void;
  reset: () => void;
  
  
  nextStep: () => void;
  prevStep: () => void;
  
  
  canProceedToStep2: () => boolean;
  canProceedToStep3: () => boolean;
}

const initialState: WizardStepData = {
  
  characterPhoto: undefined,
  characterPhotoPreview: undefined,
  referenceAudio: undefined,
  referenceText: '',
  
  
  scriptMode: 'manual',
  manualScript: undefined,
  topic: undefined,
  keywords: undefined,
  description: undefined,
  
  
  finalScript: undefined,
  generatedVideoUrl: undefined,
  isGenerating: false,
};

export const useAICloneStore = create<AICloneStore>((set, get) => ({
  ...initialState,
  currentStep: 1,
  
  setCurrentStep: (step) => set({ currentStep: step }),
  
  updateData: (data) => set((state) => ({ ...state, ...data })),
  
  reset: () => {
    
    const state = get();
    if (state.characterPhotoPreview && state.characterPhotoPreview.startsWith('blob:')) {
      URL.revokeObjectURL(state.characterPhotoPreview);
    }
    if (state.generatedVideoUrl && state.generatedVideoUrl.startsWith('blob:')) {
      URL.revokeObjectURL(state.generatedVideoUrl);
    }
    
    
    set({ ...initialState, currentStep: 1 });
  },
  
  nextStep: () => {
    const { currentStep } = get();
    if (currentStep < 3) {
      set({ currentStep: (currentStep + 1) as WizardStep });
    }
  },
  
  prevStep: () => {
    const { currentStep } = get();
    if (currentStep > 1) {
      set({ currentStep: (currentStep - 1) as WizardStep });
    }
  },
  
  canProceedToStep2: () => {
    const { characterPhoto, referenceAudio, referenceText } = get();
    return !!(characterPhoto && referenceAudio && referenceText.trim().length >= 10);
  },
  
  canProceedToStep3: () => {
    const { scriptMode, manualScript, topic } = get();
    if (scriptMode === 'manual') {
      return !!(manualScript && manualScript.trim().length >= 20);
    } else {
      return !!(topic && topic.trim().length >= 3);
    }
  },
}));
