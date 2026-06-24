import React from 'react'
import { Video, Users } from 'lucide-react'
import { RoomCard as Card } from '../components'
import Sparkline from './Sparkline'

export default function RoomCard({ room, isSelected, onSelect, historyData }) {
  const payload = room.latestPayload
  const alertLevel = payload?.population_data?.alert_level || 'NORMAL'
  const count = payload?.population_data?.current_count || 0
  const location = payload?.device_info?.location || 'Unknown Location'

  return (
    <Card
      selected={isSelected}
      status={alertLevel.toLowerCase() === 'critical' ? 'critical' : alertLevel.toLowerCase() === 'warning' ? 'warning' : 'normal'}
      onClick={onSelect}
    >
      <div className="card-header-row">
        <div className="card-title" title={room.roomId}>
          {room.roomId.replace('device:', '')}
        </div>
        <div className="card-time">
          {new Date(room.lastSeenAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
        </div>
      </div>
      <div className="card-meta">
        <Video size={11} />
        <span>{location}</span>
      </div>

      <div className="card-stats-row">
        <div className="card-metric">
          <Users size={12} />
          <span>Occupants: <strong>{count}</strong></span>
        </div>
        <span className={`card-badge ${alertLevel.toLowerCase()}`}>
          {alertLevel}
        </span>
      </div>

      <Sparkline data={historyData} />
    </Card>
  )
}
