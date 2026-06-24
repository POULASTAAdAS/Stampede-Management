import { styled, keyframes } from './stitches.config';

// ── Keyframes for smooth animations ──
export const radarSweep = keyframes({
  '0%': { transform: 'rotate(0deg)' },
  '100%': { transform: 'rotate(360deg)' },
});

export const pulseCritical = keyframes({
  '0%, 100%': { 
    borderColor: '$$color', 
    boxShadow: '0 0 6px $$colorGlow',
  },
  '50%': { 
    borderColor: 'rgba(255, 255, 255, 0.08)', 
    boxShadow: 'none',
  },
});

export const fadeIn = keyframes({
  '0%': { opacity: 0, transform: 'translateY(4px)' },
  '100%': { opacity: 1, transform: 'translateY(0)' },
});

// ── Layout Components ──
export const AppContainer = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  minHeight: '100dvh',
  width: '100%',
  overflow: 'hidden',
  background: 'radial-gradient(circle at 18% 0%, rgba(56, 189, 248, 0.10), transparent 34rem), radial-gradient(circle at 80% 0%, rgba(16, 185, 129, 0.06), transparent 28rem), $bgBase',
  color: '$textMain',
  fontFamily: '$sans',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
});

export const Header = styled('header', {
  height: '64px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '0 22px',
  background: 'rgba(16, 24, 39, 0.86)',
  borderBottom: '1px solid $border',
  backdropFilter: 'blur(18px)',
  boxShadow: '0 10px 36px rgba(0, 0, 0, 0.24)',
  zIndex: 100,
  '@bp2': {
    height: '56px',
    padding: '0 12px',
  },
});

export const BrandSection = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  minWidth: 0,
});

export const SidebarToggle = styled('button', {
  display: 'none',
  background: 'transparent',
  border: 'none',
  color: '$textMain',
  cursor: 'pointer',
  padding: '6px',
  borderRadius: '$sm',
  transition: 'background 0.2s',
  '&:hover': {
    background: '$bgHover',
  },
  '&:focus': {
    outline: 'none',
  },
  '@bp2': {
    display: 'block',
    padding: '6px',
    '& svg': {
      width: '16px !important',
      height: '16px !important',
    },
  },
});

export const BrandLogo = styled('div', {
  width: '34px',
  height: '34px',
  borderRadius: '$md',
  background: 'linear-gradient(135deg, $accent, #2563eb)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  boxShadow: '0 14px 34px rgba(37, 99, 235, 0.28)',
  transition: 'transform 0.3s ease',
  '&:hover': {
    transform: 'rotate(10deg) scale(1.05)',
  },
  '@bp2': {
    width: '30px',
    height: '30px',
  },
});

export const BrandText = styled('div', {
  '& h1': {
    fontSize: '15px',
    fontWeight: 700,
    color: '$textMain',
    letterSpacing: '-0.35px',
    lineHeight: 1.1,
    '@bp3': {
      fontSize: '12px',
    },
  },
  '& span': {
    fontSize: '9px',
    color: '$textMuted',
    fontFamily: '$mono',
    letterSpacing: '0.5px',
    '@bp2': {
      display: 'none',
    },
  },
});

export const HeaderControls = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  '@bp2': {
    gap: '6px',
  },
});

export const SystemStatus = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  background: 'rgba(7, 11, 18, 0.72)',
  padding: '8px 12px',
  borderRadius: '$round',
  border: '1px solid $border',
  transition: 'border-color 0.2s',
  '&:hover': {
    borderColor: '$borderFocus',
  },
  '@bp2': {
    display: 'none',
  },
});

export const StatusIndicator = styled('div', {
  width: '6px',
  height: '6px',
  borderRadius: '$round',
  variants: {
    state: {
      online: { background: '$colorSafe', boxShadow: '0 0 8px $colorSafe' },
      offline: { background: '$textDim' },
      simulated: { background: '$accent', boxShadow: '0 0 8px $accent' },
    },
  },
});

export const StatusLabel = styled('span', {
  fontSize: '10px',
  color: '$textMuted',
  '& strong': {
    color: '$textMain',
  },
});

export const IconOnlyBtn = styled('button', {
  background: 'rgba(7, 11, 18, 0.45)',
  border: '1px solid $border',
  color: '$textMuted',
  width: '34px',
  height: '34px',
  borderRadius: '$md',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    color: '$textMain',
    background: '$bgHover',
    borderColor: '$textDim',
  },
  '&:active': {
    transform: 'scale(0.92)',
  },
  '@bp2': {
    width: '30px',
    height: '30px',
    borderRadius: '$sm',
    '& svg': {
      width: '12px !important',
      height: '12px !important',
    },
  },
  variants: {
    active: {
      true: {
        color: '$accent',
        borderColor: '$accent',
        background: '$accentGlow',
      },
    },
  },
});

export const DashboardBody = styled('div', {
  display: 'flex',
  flex: 1,
  minHeight: 0,
  overflow: 'hidden',
  position: 'relative',
});

// ── Sidebar Drawer ──
export const SidebarBackdrop = styled('div', {
  position: 'absolute',
  inset: '64px 0 0 0',
  background: 'rgba(0, 0, 0, 0.56)',
  zIndex: 998,
  backdropFilter: 'blur(8px)',
  animation: `${fadeIn} 0.2s cubic-bezier(0.4, 0, 0.2, 1)`,
  '@bp2': {
    position: 'fixed',
    inset: '0 0 0 0',
    zIndex: 1090,
  },
});

export const Sidebar = styled('aside', {
  width: '292px',
  minWidth: '292px',
  background: 'rgba(16, 24, 39, 0.82)',
  borderRight: '1px solid $border',
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
  backdropFilter: 'blur(18px)',
  transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '@bp2': {
    position: 'fixed',
    top: 0,
    bottom: 0,
    left: 0,
    width: '100%',
    height: '100%',
    zIndex: 1100,
    transform: 'translateX(-100%)',
    borderRight: 'none',
  },
  variants: {
    open: {
      true: {
        transform: 'translateX(0)',
      },
    },
  },
});

export const SidebarSearchWrap = styled('div', {
  padding: '14px 12px',
  borderBottom: '1px solid $border',
});

export const SearchContainer = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  background: 'rgba(7, 11, 18, 0.72)',
  border: '1px solid $border',
  borderRadius: '$md',
  padding: '9px 11px',
  transition: 'border-color 0.2s',
  '&:focus-within': {
    borderColor: '$borderFocus',
  },
  '& input': {
    flex: 1,
    background: 'transparent',
    border: 'none',
    color: '$textMain',
    fontSize: '12px',
    outline: 'none',
  },
});

export const SidebarTitle = styled('div', {
  padding: '16px 14px 8px',
  fontSize: '10px',
  fontWeight: 700,
  textTransform: 'uppercase',
  color: '$textMuted',
  letterSpacing: '0.8px',
});

export const RoomsList = styled('div', {
  flex: 1,
  overflowY: 'auto',
  padding: '8px 10px 14px',
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
});

export const RoomCard = styled('div', {
  background: 'linear-gradient(180deg, rgba(23, 34, 53, 0.78), rgba(12, 18, 30, 0.78))',
  border: '1px solid $border',
  borderRadius: '$lg',
  padding: '14px',
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  animation: `${fadeIn} 0.3s ease`,
  '&:hover': {
    borderColor: '$textDim',
    transform: 'translateY(-1px)',
  },
  '&:active': {
    transform: 'scale(0.97)',
  },
  variants: {
    selected: {
      true: {
        borderColor: '$accent',
        background: 'linear-gradient(180deg, rgba(56, 189, 248, 0.14), rgba(23, 34, 53, 0.86))',
        boxShadow: '0 16px 34px rgba(0,0,0,0.24)',
      },
    },
    status: {
      normal: {},
      warning: {
        '$$color': '$colors$colorWarning',
        '$$colorGlow': '$colors$colorWarningBg',
        animation: `${pulseCritical} 3s infinite`,
      },
      critical: {
        '$$color': '$colors$colorDanger',
        '$$colorGlow': '$colors$colorDangerBg',
        animation: `${pulseCritical} 2s infinite`,
      },
    },
  },
});

// ── Content Layout ──
export const ContentArea = styled('main', {
  flex: 1,
  overflowY: 'auto',
  padding: '18px',
  display: 'flex',
  flexDirection: 'column',
  gap: '18px',
  '@bp2': {
    padding: '12px',
    gap: '12px',
  },
});

export const DetailHeaderPanel = styled('div', {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  background: 'linear-gradient(135deg, rgba(23, 34, 53, 0.86), rgba(16, 24, 39, 0.82))',
  border: '1px solid $border',
  padding: '16px 18px',
  borderRadius: '$lg',
  gap: '12px',
  boxShadow: '0 16px 40px rgba(0, 0, 0, 0.18)',
  animation: `${fadeIn} 0.3s cubic-bezier(0.4, 0, 0.2, 1)`,
  '@bp2': {
    flexDirection: 'column',
    alignItems: 'flex-start',
    padding: '12px',
  },
});

export const MetricsRow = styled('div', {
  display: 'grid',
  gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
  gap: '14px',
  '@bp1': {
    gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
  },
  '@bp3': {
    gridTemplateColumns: '1fr',
  },
});

export const MetricCard = styled('div', {
  background: 'linear-gradient(180deg, rgba(23, 34, 53, 0.82), rgba(13, 20, 33, 0.86))',
  border: '1px solid $border',
  borderRadius: '$lg',
  padding: '16px',
  display: 'flex',
  alignItems: 'center',
  gap: '14px',
  minWidth: 0,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  animation: `${fadeIn} 0.4s ease`,
  '&:hover': {
    borderColor: '$borderFocus',
    transform: 'translateY(-2px)',
    boxShadow: '0 16px 34px rgba(0, 0, 0, 0.22)',
  },
});

export const MetricIconBox = styled('div', {
  width: '42px',
  height: '42px',
  borderRadius: '$md',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  variants: {
    color: {
      blue: { background: '$accentGlow', color: '$accent' },
      cyan: { background: 'rgba(56, 189, 248, 0.08)', color: '#38bdf8' },
      orange: { background: '$colorWarningBg', color: '$colorWarning' },
      red: { background: '$colorDangerBg', color: '$colorDanger' },
    },
  },
});

export const MetricValue = styled('span', {
  fontSize: '22px',
  fontWeight: 700,
  fontFamily: '$mono',
  display: 'block',
});

export const MetricName = styled('span', {
  fontSize: '9px',
  textTransform: 'uppercase',
  color: '$textMuted',
  letterSpacing: '0.5px',
});

export const VisualizersGrid = styled('div', {
  display: 'grid',
  gridTemplateColumns: 'minmax(0, 1.05fr) minmax(0, 0.95fr)',
  gap: '16px',
  '@bp1': {
    gridTemplateColumns: '1fr',
  },
});

export const DetailsRow = styled('div', {
  display: 'grid',
  gridTemplateColumns: '1fr',
  gap: '16px',
  '@bp1': {
    gridTemplateColumns: '1fr',
  },
});

export const DashboardPanel = styled('div', {
  background: 'linear-gradient(180deg, rgba(16, 24, 39, 0.92), rgba(12, 18, 30, 0.92))',
  border: '1px solid $border',
  borderRadius: '$lg',
  padding: '18px',
  display: 'flex',
  flexDirection: 'column',
  boxShadow: '0 18px 42px rgba(0, 0, 0, 0.20)',
  transition: 'border-color 0.2s, transform 0.2s, box-shadow 0.2s',
  animation: `${fadeIn} 0.5s ease`,
  '&:hover': {
    borderColor: '$borderFocus',
    boxShadow: '0 22px 48px rgba(0, 0, 0, 0.24)',
  },
  '@bp2': {
    padding: '14px',
  },
});

export const RadarContainerOuter = styled('div', {
  position: 'relative',
  width: '100%',
  aspectRatio: '16/9',
  background: 'radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.05), transparent 42%), #05080d',
  borderRadius: '$md',
  border: '1px solid $border',
  overflow: 'hidden',
  minHeight: '360px',
  transition: 'border-color 0.2s',
  '&:hover': {
    borderColor: '$borderFocus',
  },
  '@bp2': {
    minHeight: '280px',
  },
  '@bp3': {
    minHeight: '235px',
  },
});

export const RadarSweepBeam = styled('div', {
  position: 'absolute',
  top: '50%',
  left: '50%',
  width: '150%',
  height: '150%',
  background: 'conic-gradient(from 0deg, rgba(56, 189, 248, 0.18) 0deg, transparent 58deg, transparent 360deg)',
  transformOrigin: '0% 0%',
  pointerEvents: 'none',
  animation: `${radarSweep} 8s linear infinite`,
  display: 'none',
  variants: {
    active: {
      true: { display: 'block' },
    },
  },
});

export const GridWrapper = styled('div', {
  display: 'grid',
  gap: '5px',
  padding: '8px',
  background: '#05080d',
  border: '1px solid $border',
  borderRadius: '$md',
  transition: 'all 0.3s ease',
  boxShadow: 'inset 0 2px 18px rgba(0,0,0,0.36)',
});

export const GridCellBox = styled('div', {
  aspectRatio: 1,
  borderRadius: '$sm',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '11px',
  fontWeight: 600,
  fontFamily: '$mono',
  cursor: 'default',
  position: 'relative',
  transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    transform: 'scale(1.08)',
    zIndex: 10,
    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
  },
  '& .tooltip': {
    visibility: 'hidden',
    position: 'absolute',
    bottom: 'calc(100% + 6px)',
    left: '50%',
    transform: 'translateX(-50%)',
    background: '$bgCard',
    border: '1px solid $border',
    padding: '8px 12px',
    borderRadius: '$md',
    whiteSpace: 'nowrap',
    fontSize: '10px',
    color: '$textMain',
    zIndex: 100,
    pointerEvents: 'none',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    '& strong': {
      color: '$accent',
    },
  },
  '&:hover .tooltip': {
    visibility: 'visible',
  },
  variants: {
    level: {
      normal: { background: '$colorSafeBg', color: '$colorSafe' },
      warning: { background: '$colorWarningBg', color: '$colorWarning' },
      critical: { background: '$colorDangerBg', color: '$colorDanger' },
    },
  },
});
