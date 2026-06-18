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
  width: '100%',
  overflow: 'hidden',
  backgroundColor: '$bgBase',
  color: '$textMain',
  fontFamily: '$sans',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
});

export const Header = styled('header', {
  height: '56px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '0 16px',
  background: '$bgSurface',
  borderBottom: '1px solid $border',
  zIndex: 100,
  '@bp2': {
    height: '48px',
    padding: '0 10px',
  },
});

export const BrandSection = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
});

export const SidebarToggle = styled('button', {
  display: 'none',
  background: 'transparent',
  border: 'none',
  color: '$textMain',
  cursor: 'pointer',
  padding: '4px',
  borderRadius: '$sm',
  transition: 'background 0.2s',
  '&:hover': {
    background: '$bgHover',
  },
  '@bp2': {
    display: 'block',
    padding: '2px',
    '& svg': {
      width: '14px !important',
      height: '14px !important',
    },
  },
});

export const BrandLogo = styled('div', {
  width: '28px',
  height: '28px',
  borderRadius: '$sm',
  background: 'linear-gradient(135deg, $accent, #7c3aed)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  boxShadow: '0 4px 12px rgba(94, 124, 240, 0.25)',
  transition: 'transform 0.3s ease',
  '&:hover': {
    transform: 'rotate(10deg) scale(1.05)',
  },
  '@bp2': {
    width: '24px',
    height: '24px',
  },
});

export const BrandText = styled('div', {
  '& h1': {
    fontSize: '14px',
    fontWeight: 600,
    color: '$textMain',
    letterSpacing: '-0.2px',
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
  gap: '6px',
  background: '$bgBase',
  padding: '6px 12px',
  borderRadius: '$md',
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

export const ToggleDemoBtn = styled('button', {
  background: '$accentGlow',
  color: '$textMain',
  border: '1px solid $accent',
  padding: '6px 12px',
  fontSize: '10px',
  borderRadius: '$md',
  cursor: 'pointer',
  fontWeight: 500,
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    background: '$bgHover',
    transform: 'translateY(-1px)',
  },
  '&:active': {
    transform: 'translateY(0)',
  },
  '@bp2': {
    padding: '4px 8px',
    fontSize: '9px',
  },
  '@bp3': {
    padding: '3px 6px',
    fontSize: '8px',
  },
  variants: {
    active: {
      true: {
        background: '$accent',
        boxShadow: '0 4px 12px rgba(94, 124, 240, 0.3)',
      },
    },
  },
});

export const IconOnlyBtn = styled('button', {
  background: 'transparent',
  border: '1px solid $border',
  color: '$textMuted',
  width: '28px',
  height: '28px',
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
  '@bp2': {
    width: '24px',
    height: '24px',
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
  overflow: 'hidden',
  position: 'relative',
});

// ── Sidebar Drawer ──
export const SidebarBackdrop = styled('div', {
  position: 'absolute',
  inset: '56px 0 0 0',
  background: 'rgba(0, 0, 0, 0.4)',
  zIndex: 998,
  backdropFilter: 'blur(8px)',
  animation: `${fadeIn} 0.2s cubic-bezier(0.4, 0, 0.2, 1)`,
});

export const Sidebar = styled('aside', {
  width: '260px',
  minWidth: '260px',
  background: '$bgSurface',
  borderRight: '1px solid $border',
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
  transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '@bp2': {
    position: 'absolute',
    top: '56px',
    bottom: 0,
    left: 0,
    zIndex: 999,
    transform: 'translateX(-100%)',
    boxShadow: '8px 0 24px rgba(0, 0, 0, 0.3)',
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
  padding: '10px',
  borderBottom: '1px solid $border',
});

export const SearchContainer = styled('div', {
  display: 'flex',
  alignItems: 'center',
  gap: '6px',
  background: '$bgBase',
  border: '1px solid $border',
  borderRadius: '$md',
  padding: '6px 10px',
  transition: 'border-color 0.2s',
  '&:focus-within': {
    borderColor: '$borderFocus',
  },
  '& input': {
    flex: 1,
    background: 'transparent',
    border: 'none',
    color: '$textMain',
    fontSize: '11px',
    outline: 'none',
  },
});

export const SidebarTitle = styled('div', {
  padding: '12px 12px 6px',
  fontSize: '9px',
  fontWeight: 600,
  textTransform: 'uppercase',
  color: '$textMuted',
  letterSpacing: '0.5px',
});

export const RoomsList = styled('div', {
  flex: 1,
  overflowY: 'auto',
  padding: '8px',
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
});

export const RoomCard = styled('div', {
  background: '$bgBase',
  border: '1px solid $border',
  borderRadius: '$md',
  padding: '12px',
  cursor: 'pointer',
  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
  animation: `${fadeIn} 0.3s ease`,
  '&:hover': {
    borderColor: '$textDim',
    transform: 'translateY(-1px)',
  },
  variants: {
    selected: {
      true: {
        borderColor: '$accent',
        background: '$bgHover',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
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
  padding: '16px',
  display: 'flex',
  flexDirection: 'column',
  gap: '16px',
  '@bp2': {
    padding: '12px',
    gap: '12px',
  },
});

export const DetailHeaderPanel = styled('div', {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  background: '$bgSurface',
  border: '1px solid $border',
  padding: '12px 16px',
  borderRadius: '$lg',
  gap: '12px',
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
  animation: `${fadeIn} 0.3s cubic-bezier(0.4, 0, 0.2, 1)`,
  '@bp2': {
    flexDirection: 'column',
    alignItems: 'flex-start',
    padding: '12px',
  },
});

export const MetricsRow = styled('div', {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
  gap: '12px',
  '@bp3': {
    gridTemplateColumns: '1fr',
  },
});

export const MetricCard = styled('div', {
  background: '$bgSurface',
  border: '1px solid $border',
  borderRadius: '$lg',
  padding: '14px',
  display: 'flex',
  alignItems: 'center',
  gap: '12px',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  animation: `${fadeIn} 0.4s ease`,
  '&:hover': {
    borderColor: '$borderFocus',
    transform: 'translateY(-2px)',
    boxShadow: '0 6px 20px rgba(0, 0, 0, 0.15)',
  },
});

export const MetricIconBox = styled('div', {
  width: '36px',
  height: '36px',
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
  fontSize: '20px',
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
  gridTemplateColumns: '1fr 1fr',
  gap: '16px',
  '@bp1': {
    gridTemplateColumns: '1fr',
  },
});

export const DetailsRow = styled('div', {
  display: 'grid',
  gridTemplateColumns: '1.2fr 0.8fr',
  gap: '16px',
  '@bp1': {
    gridTemplateColumns: '1fr',
  },
});

export const DashboardPanel = styled('div', {
  background: '$bgSurface',
  border: '1px solid $border',
  borderRadius: '$lg',
  padding: '16px',
  display: 'flex',
  flexDirection: 'column',
  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
  transition: 'border-color 0.2s',
  animation: `${fadeIn} 0.5s ease`,
  '&:hover': {
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
});

export const RadarContainerOuter = styled('div', {
  position: 'relative',
  width: '100%',
  aspectRatio: '16/9',
  background: '$bgBase',
  borderRadius: '$md',
  border: '1px solid $border',
  overflow: 'hidden',
  transition: 'border-color 0.2s',
  '&:hover': {
    borderColor: '$borderFocus',
  },
});

export const RadarSweepBeam = styled('div', {
  position: 'absolute',
  top: '50%',
  left: '50%',
  width: '150%',
  height: '150%',
  background: 'conic-gradient(from 0deg, rgba(94, 124, 240, 0.1) 0deg, transparent 60deg, transparent 360deg)',
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
  gap: '3px',
  padding: '6px',
  background: '$bgBase',
  border: '1px solid $border',
  borderRadius: '$md',
  transition: 'all 0.3s ease',
  boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.2)',
});

export const GridCellBox = styled('div', {
  aspectRatio: 1,
  borderRadius: '$sm',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '10px',
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

export const LogConsole = styled('div', {
  background: '$bgBase',
  borderRadius: '$md',
  border: '1px solid $border',
  padding: '10px',
  fontFamily: '$mono',
  fontSize: '9px',
  color: '$colorSafe',
  height: '120px',
  overflowY: 'auto',
  display: 'flex',
  flexDirection: 'column',
  gap: '4px',
  boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.2)',
});
