package com.poulastaa.backend

import java.time.Instant

data class Room(
    val roomId: String,
    val identifierType: RoomIdentifierType,
    val identifierValue: String,
    val createdAt: Instant = Instant.now(),
    var lastSeenAt: Instant = createdAt,
    var messageCount: Long = 0,
)

enum class RoomIdentifierType {
    DEVICE_ID,
    MAC_ADDRESS,
}
