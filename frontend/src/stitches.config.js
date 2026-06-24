import { createStitches } from '@stitches/react';

export const {
  styled,
  css,
  globalCss,
  keyframes,
  theme,
  createTheme,
  config,
} = createStitches({
  theme: {
    colors: {
      bgBase: '#070b13',
      bgSurface: '#0e1626',
      bgCard: '#172237',
      bgHover: '#22304d',
      border: 'rgba(212, 175, 55, 0.12)',
      borderFocus: 'rgba(212, 175, 55, 0.4)',
      textMain: '#f8fafc',
      textMuted: '#94a3b8',
      textDim: '#475569',
      accent: '#d4af37',
      accentGlow: 'rgba(212, 175, 55, 0.15)',
      colorSafe: '#10b981',
      colorSafeBg: 'rgba(16, 185, 129, 0.08)',
      colorWarning: '#e5c158',
      colorWarningBg: 'rgba(229, 193, 88, 0.08)',
      colorDanger: '#ef4444',
      colorDangerBg: 'rgba(239, 68, 68, 0.1)',
    },
    space: {
      1: '4px',
      2: '8px',
      3: '12px',
      4: '16px',
      5: '24px',
    },
    radii: {
      sm: '4px',
      md: '8px',
      lg: '12px',
      round: '9999px',
    },
    fonts: {
      sans: "'Inter', sans-serif",
      mono: "'JetBrains Mono', monospace",
    },
  },
  media: {
    bp1: '(max-width: 1024px)',
    bp2: '(max-width: 768px)',
    bp3: '(max-width: 480px)',
  },
});
