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
      bgBase: '#080a10',
      bgSurface: '#0e111a',
      bgCard: '#141824',
      bgHover: '#1c2234',
      border: 'rgba(255, 255, 255, 0.06)',
      borderFocus: 'rgba(99, 131, 255, 0.3)',
      textMain: '#f3f4f6',
      textMuted: '#9ca3af',
      textDim: '#4b5563',
      accent: '#5e7cf0',
      accentGlow: 'rgba(94, 124, 240, 0.15)',
      colorSafe: '#10b981',
      colorSafeBg: 'rgba(16, 185, 129, 0.08)',
      colorWarning: '#f59e0b',
      colorWarningBg: 'rgba(245, 158, 11, 0.08)',
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
