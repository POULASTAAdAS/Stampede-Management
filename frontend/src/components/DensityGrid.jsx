import { Grid } from 'lucide-react'
import { DashboardPanel, GridWrapper, GridCellBox } from '../components'

export default function DensityGrid({
  activeRoom,
  gridRows,
  gridCols,
  warningThreshold,
  criticalThreshold
}) {
  const cellsData = activeRoom.latestPayload?.population_data?.occupancy_grid?.cells || []

  return (
    <DashboardPanel>
      <div className="panel-header">
        <div className="panel-title">
          <Grid size={14} />
          <span>Occupancy Density Grid</span>
        </div>
      </div>

      <div className="heatmap-container">
        <GridWrapper
          style={{
            gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
            width: '100%',
            maxWidth: `min(100%, ${gridCols * 70}px)`,
            aspectRatio: `${gridCols} / ${gridRows}`
          }}
        >
          {/* Render Cells */}
          {Array.from({ length: gridRows }).map((_, rIdx) => {
            return Array.from({ length: gridCols }).map((_, cIdx) => {
              const cellData = cellsData.find(
                c => c.row === rIdx && c.col === cIdx
              ) || { occupant_count: 0, density: 0.0, alert_level: 'NORMAL' }

              const style = {
                '--intensity': Math.min(cellData.density, 1.0)
              }

              return (
                <GridCellBox
                  key={`${rIdx}-${cIdx}`}
                  level={cellData.alert_level.toLowerCase()}
                  style={style}
                >
                  <span>{Math.round(cellData.occupant_count)}</span>

                  <div className="tooltip">
                    <strong>Cell [{rIdx}, {cIdx}]</strong><br />
                    Occupants: {cellData.occupant_count}<br />
                    Density: {Math.round(cellData.density * 100)}%<br />
                    Status: {cellData.alert_level}
                  </div>
                </GridCellBox>
              )
            })
          })}
        </GridWrapper>

        {/* Heatmap Legend */}
        <div className="heatmap-legend">
          <div className="legend-card">
            <div className="legend-box" style={{ background: 'var(--color-safe-bg)', border: '1px solid var(--color-safe)' }}></div>
            <span>Normal (&lt;{Math.round(warningThreshold * 100)}%)</span>
          </div>
          <div className="legend-card">
            <div className="legend-box" style={{ background: 'var(--color-warning-bg)', border: '1px solid var(--color-warning)' }}></div>
            <span>Warning ({Math.round(warningThreshold * 100)}%+)</span>
          </div>
          <div className="legend-card">
            <div className="legend-box" style={{ background: 'var(--color-danger-bg)', border: '1px solid var(--color-danger)' }}></div>
            <span>Critical (&gt;{Math.round(criticalThreshold * 100)}%)</span>
          </div>
        </div>
      </div>
    </DashboardPanel>
  )
}
