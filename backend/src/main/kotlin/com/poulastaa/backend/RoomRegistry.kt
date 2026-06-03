package com.poulastaa.backend

import org.springframework.stereotype.Service
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CopyOnWriteArrayList

fun interface RoomUpdateListener {
    fun onRoomUpdate(room: Room, rawPayload: String)
}

@Service
class RoomRegistry {
    private val rooms = ConcurrentHashMap<String, Room>()
    private val latestPayloads = ConcurrentHashMap<String, String>()
    private val listeners = CopyOnWriteArrayList<RoomUpdateListener>()

    fun addListener(listener: RoomUpdateListener) {
        listeners.add(listener)
    }

    fun createOrTouchRoom(identifier: RoomIdentifier, rawPayload: String? = null): Room {
        val room = rooms.compute(identifier.roomId) { _, existing ->
            existing?.apply {
                lastSeenAt = Instant.now()
                messageCount += 1
            } ?: Room(
                roomId = identifier.roomId,
                identifierType = identifier.type,
                identifierValue = identifier.value,
                messageCount = 1,
            )
        }!!

        if (rawPayload != null) {
            latestPayloads[identifier.roomId] = rawPayload
            listeners.forEach { it.onRoomUpdate(room, rawPayload) }
        }

        return room
    }

    fun getLatestPayload(roomId: String): String? = latestPayloads[roomId]

    fun listRooms(): List<Room> = rooms.values.sortedBy { it.roomId }
}

data class RoomIdentifier(
    val type: RoomIdentifierType,
    val value: String,
) {
    val roomId: String = when (type) {
        RoomIdentifierType.DEVICE_ID -> "device:$value"
        RoomIdentifierType.MAC_ADDRESS -> "mac:${normalizeMac(value)}"
    }

    companion object {
        private fun normalizeMac(macAddress: String): String =
            macAddress.trim().lowercase().replace("-", ":")
    }
}
