// SwasthyaAI Mobile Theme
// Premium healthcare design system with forest green, teal, emerald palette

import { Theme } from '../types';

export const colors = {
  // Primary - Deep Forest Green
  primary: '#0F3D3E',
  primaryLight: '#1A5C5D',
  primaryDark: '#082627',

  // Secondary - Rich Teal
  secondary: '#0D9488',
  secondaryLight: '#14B8A6',
  secondaryDark: '#0F766E',

  // Accent - Emerald
  accent: '#10B981',
  accentLight: '#34D399',
  accentDark: '#059669',

  // Warm Ivory/Cream
  background: '#FDFBF7',
  surface: '#FFFFFF',
  surfaceVariant: '#F5F3EF',
  card: '#FFFFFF',

  // Midnight Navy for AI surfaces
  aiSurface: '#0F172A',
  aiSurfaceVariant: '#1E293B',

  // Text
  text: '#1A1A1A',
  textSecondary: '#4A4A4A',
  textMuted: '#7A7A7A',
  textOnPrimary: '#FFFFFF',
  textOnSecondary: '#FFFFFF',

  // Borders
  border: '#E5E5E5',
  borderLight: '#F0F0F0',

  // Status
  success: '#10B981',
  successLight: '#D1FAE5',
  warning: '#F59E0B',
  warningLight: '#FEF3C7',
  error: '#EF4444',
  errorLight: '#FEE2E2',
  info: '#3B82F6',
  infoLight: '#DBEAFE',

  // Emergency
  emergency: '#DC2626',
  emergencyLight: '#FEF2F2',

  // Lavender & Coral accents
  lavender: '#A78BFA',
  lavenderLight: '#EDE9FE',
  coral: '#F97316',
  coralLight: '#FFEDD5',

  // Gradients
  gradientPrimary: ['#0F3D3E', '#0D9488'] as const,
  gradientSecondary: ['#0D9488', '#10B981'] as const,
  gradientAccent: ['#10B981', '#34D399'] as const,
  gradientAI: ['#0F172A', '#1E293B'] as const,
  gradientWarm: ['#FDFBF7', '#F5F3EF'] as const,
  gradientEmergency: ['#DC2626', '#EF4444'] as const,
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const typography = {
  h1: { fontSize: 34, fontWeight: '700' as const, lineHeight: 42 },
  h2: { fontSize: 28, fontWeight: '700' as const, lineHeight: 36 },
  h3: { fontSize: 22, fontWeight: '600' as const, lineHeight: 30 },
  h4: { fontSize: 18, fontWeight: '600' as const, lineHeight: 26 },
  body: { fontSize: 16, fontWeight: '400' as const, lineHeight: 24 },
  bodySmall: { fontSize: 14, fontWeight: '400' as const, lineHeight: 20 },
  caption: { fontSize: 12, fontWeight: '400' as const, lineHeight: 16 },
  button: { fontSize: 16, fontWeight: '600' as const, lineHeight: 24 },
};

export const borderRadius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 9999,
};

export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 8,
  },
  xl: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.15,
    shadowRadius: 24,
    elevation: 12,
  },
};

export const theme: Theme = {
  colors,
  spacing,
  typography,
  borderRadius,
  shadows,
};

export type { Theme } from '../types';