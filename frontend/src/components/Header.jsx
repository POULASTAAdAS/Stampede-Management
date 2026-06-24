import React from 'react'
import { ShieldAlert, Menu, VolumeX, Volume2 } from 'lucide-react'
import {
  Header as HeaderWrapper, BrandSection, SidebarToggle, BrandLogo, BrandText,
  HeaderControls, SystemStatus, StatusIndicator, StatusLabel, IconOnlyBtn
} from '../components'

export default function Header({
  isConnected,
  isAudioMuted,
  setIsAudioMuted,
  isSidebarOpen,
  setIsSidebarOpen,
  addLog
}) {
  return (
    <HeaderWrapper>
      <BrandSection>
        <SidebarToggle 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          aria-label="Toggle Sidebar"
        >
          <Menu size={16} />
        </SidebarToggle>
        <BrandLogo style={{ fontSize: '15px', fontWeight: '800', fontFamily: 'var(--font-mono)', color: '#fff' }}>
          S
        </BrandLogo>
        <BrandText>
          <h1>STAMPEDE MANAGEMENT SYSTEM</h1>
          <span>SPATIAL DENSITY telemetry gateway</span>
        </BrandText>
      </BrandSection>

      <HeaderControls>
        <SystemStatus>
          <StatusIndicator state={isConnected ? 'online' : 'offline'} />
          <StatusLabel>
            GATEWAY: <strong>{isConnected ? 'ONLINE' : 'OFFLINE'}</strong>
          </StatusLabel>
        </SystemStatus>

        <IconOnlyBtn
          active={!isAudioMuted}
          onClick={() => {
            setIsAudioMuted(!isAudioMuted)
            addLog(!isAudioMuted ? "Audio alerts enabled" : "Audio warnings muted", "system")
          }}
          title={isAudioMuted ? "Unmute Voice Alerter" : "Mute Voice Alerter"}
        >
          {isAudioMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
        </IconOnlyBtn>
      </HeaderControls>
    </HeaderWrapper>
  )
}
