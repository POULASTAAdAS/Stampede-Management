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
      bgBase: '#070b12',
      bgSurface: '#101827',
      bgCard: '#172235',
      bgHover: '#1d2b42',
      border: 'rgba(148, 163, 184, 0.16)',
      borderFocus: 'rgba(56, 189, 248, 0.45)',
      textMain: '#f8fafc',
      textMuted: '#9aa9bd',
      textDim: '#5b6b80',
      accent: '#38bdf8',
      accentGlow: 'rgba(56, 189, 248, 0.16)',
      colorSafe: '#10b981',
      colorSafeBg: 'rgba(16, 185, 129, 0.11)',
      colorWarning: '#f59e0b',
      colorWarningBg: 'rgba(245, 158, 11, 0.12)',
      colorDanger: '#f43f5e',
      colorDangerBg: 'rgba(244, 63, 94, 0.13)',
    },
    space: {
      1: '4px',
      2: '8px',
      3: '12px',
      4: '16px',
      5: '24px',
    },
    radii: {
      sm: '6px',
      md: '10px',
      lg: '16px',
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
