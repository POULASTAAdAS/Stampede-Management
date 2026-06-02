package com.poulastaa.backend

import org.springframework.stereotype.Service
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap

@Service
class RoomRegistry {
    private val rooms = ConcurrentHashMap<String, Room>()

    fun createOrTouchRoom(identifier: RoomIdentifier): Room {
        return rooms.compute(identifier.roomId) { _, existing ->
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
    }

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
