import React from 'react'
import { Map, RefreshCw } from 'lucide-react'
import { DashboardPanel, RadarContainerOuter, RadarSweepBeam, IconOnlyBtn } from '../components'

export default function RadarScope({
  isRadarSweep,
  setIsRadarSweep,
  activeRoom,
  selectedTrackId,
  setSelectedTrackId
}) {
  const trackedPersons = activeRoom.latestPayload?.population_data?.tracked_persons || []
  const selectedPerson = trackedPersons.find(p => p.track_id === selectedTrackId)

  return (
    <DashboardPanel>
      <div className="panel-header">
        <div className="panel-title">
          <Map size={14} />
          <span>Live Radar Positioning Scope (Bird's Eye)</span>
        </div>
        <div className="panel-actions">
          <IconOnlyBtn
            active={isRadarSweep}
            onClick={() => setIsRadarSweep(!isRadarSweep)}
            title="Toggle Radar Sweep Animation"
          >
            <RefreshCw size={12} />
          </IconOnlyBtn>
        </div>
      </div>

      <RadarContainerOuter>
        <div className="radar-grid-bg"></div>
        <RadarSweepBeam active={isRadarSweep} />

        <svg className="radar-svg" viewBox="0 0 800 600">
          {/* Radar sweep lines */}
          <g className="radar-center-circles">
            <circle cx="400" cy="300" r="100" />
            <circle cx="400" cy="300" r="200" />
            <circle cx="400" cy="300" r="280" />
            <line x1="400" y1="20" x2="400" y2="580" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1" />
            <line x1="20" y1="300" x2="780" y2="300" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="1" />
          </g>

          {/* Display tracked points */}
          {trackedPersons.map(person => {
            const isSelected = selectedTrackId === person.track_id
            const isConfirmed = person.confirmed

            return (
              <g
                key={person.track_id}
                className={`radar-track-dot ${isSelected ? 'selected' : ''}`}
                onClick={() => setSelectedTrackId(person.track_id)}
              >
                {/* Glow */}
                <circle
                  cx={person.world_x}
                  cy={person.world_y}
                  r={isSelected ? 16 : 10}
                  fill={isSelected ? 'rgba(212, 175, 55, 0.25)' : 'rgba(255, 255, 255, 0.03)'}
                />
                {/* Core */}
                <circle
                  cx={person.world_x}
                  cy={person.world_y}
                  r={isSelected ? 6 : 4}
                  fill={isSelected ? 'var(--accent)' : isConfirmed ? 'var(--color-safe)' : 'var(--text-dim)'}
                />
                {/* Track Label text */}
                <text
                  x={person.world_x + 8}
                  y={person.world_y - 8}
                  fill={isSelected ? 'var(--accent)' : 'var(--text-muted)'}
                  fontSize="9px"
                  className="radar-track-label"
                >
                  #{person.track_id}
                </text>
              </g>
            )
          })}
        </svg>

        {selectedPerson && (
          <div className="radar-hud-overlay">
            <div className="hud-header">
              <span className="hud-tag">TARGET TRACK #{selectedPerson.track_id}</span>
              <span className={`hud-status ${selectedPerson.confirmed ? 'confirmed' : 'pending'}`}>
                {selectedPerson.confirmed ? 'CONFIRMED VEC' : 'PENDING VEC'}
              </span>
            </div>
            <div className="hud-grid">
              <div className="hud-item">
                <span className="hud-label">CONFIDENCE</span>
                <span className="hud-val">{Math.round(selectedPerson.confidence * 100)}%</span>
              </div>
              <div className="hud-item">
                <span className="hud-label">PERSISTENCE AGE</span>
                <span className="hud-val">{selectedPerson.age} frames</span>
              </div>
              <div className="hud-item">
                <span className="hud-label">COORDINATES</span>
                <span className="hud-val">[{Math.round(selectedPerson.world_x)}, {Math.round(selectedPerson.world_y)}]</span>
              </div>
            </div>
          </div>
        )}
      </RadarContainerOuter>
    </DashboardPanel>
  )
}
