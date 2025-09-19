import { z } from "zod";
import type { TFunction } from 'i18next';

export const getRegisterSchema = (t: TFunction) => z.object({
  email: z.string()
    .min(1, t('auth:validation.emailRequired'))
    .email(t('auth:validation.emailInvalid')),
  password: z.string()
    .min(1, t('auth:validation.passwordRequired'))
    .min(8, t('auth:validation.passwordMinLength')),
  profile: z.object({
    full_name: z.string()
      .min(1, t('auth:validation.fullNameRequired'))
      .min(2, t('auth:validation.fullNameMinLength')),
  }),
});

export const getLoginSchema = (t: TFunction) => z.object({
  email: z.string()
    .min(1, t('auth:validation.emailRequired'))
    .email(t('auth:validation.emailInvalid')),
  password: z.string()
    .min(1, t('auth:validation.passwordRequired'))
    .min(8, t('auth:validation.passwordMinLength'))
});

// Legacy schemas for backward compatibility
export const registerSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  profile: z.object({
    full_name: z.string().min(1, "Full name is required"),
  }),
});

export const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters")
});

export type RegisterFormData = z.infer<typeof registerSchema>;
export type LoginFormData = z.infer<typeof loginSchema>;
