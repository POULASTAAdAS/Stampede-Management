import { Users } from 'lucide-react'
import { DashboardPanel } from '../components'

export default function TrackedTable({
  activeRoom,
  selectedTrackId,
  setSelectedTrackId
}) {
  const trackedPersons = activeRoom.latestPayload?.population_data?.tracked_persons || []

  return (
    <DashboardPanel>
      <div className="panel-header">
        <div className="panel-title">
          <Users size={14} />
          <span>Tracked Crowd Entities</span>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="cyber-table">
          <thead>
            <tr>
              <th>Track</th>
              <th>Status</th>
              <th>Confidence</th>
              <th>Age</th>
              <th>Position</th>
            </tr>
          </thead>
          <tbody>
            {trackedPersons.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                  No tracked occupants in the current camera field.
                </td>
              </tr>
            ) : (
              trackedPersons.map(person => {
                const isSelected = selectedTrackId === person.track_id
                const confidencePercent = Math.round((person.confidence || 0) * 100)
                
                // Set indicator colors based on confidence thresholds
                let confColor = 'var(--color-safe)'
                if (confidencePercent < 75) confColor = 'var(--color-warning)'
                if (confidencePercent < 50) confColor = 'var(--color-danger)'

                return (
                  <tr
                    key={person.track_id}
                    className={isSelected ? 'selected' : ''}
                    onClick={() => setSelectedTrackId(person.track_id)}
                  >
                    <td><strong style={{ color: 'var(--accent)' }}>#{person.track_id}</strong></td>
                    <td className={person.confirmed ? 'txt-confirmed' : 'txt-pending'}>
                      {person.confirmed ? 'CONFIRMED' : 'PENDING'}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ width: '48px', height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${confidencePercent}%`, height: '100%', background: confColor, borderRadius: '3px' }} />
                        </div>
                        <span style={{ fontSize: '10px', fontWeight: '600', color: confColor }}>{confidencePercent}%</span>
                      </div>
                    </td>
                    <td>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: 'var(--text-muted)' }}>
                        <span style={{ fontFamily: 'var(--font-mono)' }}>{person.age}</span>
                        <span style={{ opacity: 0.5, fontSize: '8px' }}>f</span>
                      </span>
                    </td>
                    <td>{Math.round(person.world_x)}px, {Math.round(person.world_y)}px</td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </DashboardPanel>
  )
}
