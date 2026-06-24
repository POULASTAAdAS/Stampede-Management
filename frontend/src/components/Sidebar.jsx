import React from 'react'
import { Search, ArrowLeft } from 'lucide-react'
import {
  Sidebar as SidebarWrapper, SidebarSearchWrap, SearchContainer, SidebarTitle, RoomsList
} from '../components'
import RoomCard from './RoomCard'

export default function Sidebar({
  isOpen,
  searchQuery,
  setSearchQuery,
  filteredRooms,
  selectedRoomId,
  handleSelectRoom,
  history,
  onClose
}) {
  return (
    <SidebarWrapper open={isOpen}>
      <div className="sidebar-mobile-header">
        <button className="sidebar-back-btn" onClick={onClose} aria-label="Go Back">
          <ArrowLeft size={18} />
        </button>
        <span className="sidebar-mobile-title">Devices & Rooms</span>
      </div>

      <SidebarSearchWrap>
        <SearchContainer>
          <Search size={14} style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search rooms, device IDs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </SearchContainer>
      </SidebarSearchWrap>

      <SidebarTitle>Monitoring Rooms ({filteredRooms.length})</SidebarTitle>

      <RoomsList>
        {filteredRooms.length === 0 ? (
          <div className="no-devices">No active rooms found. Run detection clients to register.</div>
        ) : (
          filteredRooms.map(room => (
            <RoomCard
              key={room.roomId}
              room={room}
              isSelected={selectedRoomId === room.roomId}
              onSelect={() => handleSelectRoom(room.roomId)}
              historyData={history[room.roomId]}
            />
          ))
        )}
      </RoomsList>
    </SidebarWrapper>
  )
}
