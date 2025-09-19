import { z } from 'zod';

export const step1Schema = z.object({
  characterPhoto: z.instanceof(File, { message: 'Please upload a character photo' }),
  referenceAudio: z.instanceof(File, { message: 'Please provide a voice sample' }),
  referenceText: z.string().min(10, 'Reference text must be at least 10 characters'),
});

export const step2ManualSchema = z.object({
  scriptMode: z.literal('manual'),
  manualScript: z.string().min(20, 'Script must be at least 20 characters'),
});

export const step2AISchema = z.object({
  scriptMode: z.literal('ai-generated'),
  topic: z.string().min(3, 'Topic must be at least 3 characters'),
  keywords: z.string().optional(),
  description: z.string().optional(),
});

export const step2Schema = z.discriminatedUnion('scriptMode', [
  step2ManualSchema,
  step2AISchema,
]);

export const step3Schema = z.object({
  finalScript: z.string().min(10, 'Final script must be at least 10 characters'),
});

export type Step1Data = z.infer<typeof step1Schema>;
export type Step2Data = z.infer<typeof step2Schema>;
export type Step3Data = z.infer<typeof step3Schema>;
