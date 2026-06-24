import React from 'react'

export default function SettingsPanel({
  warningThreshold,
  setWarningThreshold,
  criticalThreshold,
  setCriticalThreshold
}) {
  return (
    <div style={{ marginTop: '16px' }}>
      <div className="setting-slider">
        <div className="slider-label">
          <span>Warning Alert Threshold</span>
          <span>{Math.round(warningThreshold * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.4"
          max="0.85"
          step="0.05"
          value={warningThreshold}
          onChange={(e) => setWarningThreshold(parseFloat(e.target.value))}
          className="slider-input"
          disabled
        />
      </div>

      <div className="setting-slider">
        <div className="slider-label">
          <span>Critical Alert Threshold</span>
          <span>{Math.round(criticalThreshold * 100)}%</span>
        </div>
        <input
          type="range"
          min="0.75"
          max="0.98"
          step="0.01"
          value={criticalThreshold}
          onChange={(e) => setCriticalThreshold(parseFloat(e.target.value))}
          className="slider-input"
          disabled
        />
      </div>
    </div>
  )
}
