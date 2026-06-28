package org.poulastaa.birds_eye

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

internal const val DefaultDashboardWsUrl = "wss://stamped.poulastaa.dev/ws-dashboard"

internal val DashboardJson = Json {
    ignoreUnknownKeys = true
    isLenient = true
}

data class DashboardState(
    val rooms: List<RoomSnapshot> = emptyList(),
    val selectedRoomId: String? = null,
    val selectedTrackId: Int? = null,
    val searchQuery: String = "",
    val history: Map<String, List<Int>> = emptyMap(),
    val isConnected: Boolean = false,
    val errorMessage: String? = null,
)

@Serializable
internal data class RoomListMessage(
    val type: String = "",
    val rooms: List<RoomSnapshot> = emptyList(),
)

@Serializable
internal data class RoomUpdateMessage(
    val type: String = "",
    val roomId: String = "",
    val data: MonitoringPayload? = null,
)

@Serializable
internal data class DashboardErrorMessage(
    val type: String = "",
    val message: String = "",
)

@Serializable
data class RoomSnapshot(
    val roomId: String = "",
    val identifierType: String = "",
    val identifierValue: String = "",
    val createdAt: String = "",
    val lastSeenAt: String = "",
    val messageCount: Long = 0,
    val latestPayload: MonitoringPayload? = null,
)

@Serializable
data class MonitoringPayload(
    @SerialName("device_info") val deviceInfo: DeviceInfo? = null,
    @SerialName("population_data") val populationData: PopulationData? = null,
    @SerialName("request_id") val requestId: String = "",
    @SerialName("captured_at") val capturedAt: String = "",
)

@Serializable
data class DeviceInfo(
    @SerialName("device_id") val deviceId: String = "",
    @SerialName("device_name") val deviceName: String = "",
    val location: String = "Unknown Location",
    @SerialName("camera_source") val cameraSource: String = "0",
    @SerialName("mac_address") val macAddress: String? = null,
    @SerialName("ip_address") val ipAddress: String? = null,
    val timestamp: String = "",
)

@Serializable
data class PopulationData(
    @SerialName("current_count") val currentCount: Int = 0,
    @SerialName("tracked_persons") val trackedPersons: List<PersonTrack> = emptyList(),
    @SerialName("occupancy_grid") val occupancyGrid: OccupancyGrid = OccupancyGrid(),
    @SerialName("alert_level") val alertLevel: String = "NORMAL",
    @SerialName("alert_message") val alertMessage: String? = null,
    @SerialName("frame_number") val frameNumber: Int = 0,
    val fps: Double = 0.0,
)

@Serializable
data class PersonTrack(
    @SerialName("track_id") val trackId: Int = 0,
    @SerialName("bounding_box") val boundingBox: BoundingBox? = null,
    val confidence: Double = 0.0,
    val age: Int = 0,
    val confirmed: Boolean = false,
    @SerialName("world_x") val worldX: Double? = null,
    @SerialName("world_y") val worldY: Double? = null,
)

@Serializable
data class BoundingBox(
    val x: Int = 0,
    val y: Int = 0,
    val width: Int = 0,
    val height: Int = 0,
)

@Serializable
data class OccupancyGrid(
    val rows: Int = 5,
    val cols: Int = 5,
    val cells: List<GridCell> = emptyList(),
    @SerialName("total_occupants") val totalOccupants: Int = 0,
    @SerialName("average_density") val averageDensity: Double = 0.0,
)

@Serializable
data class GridCell(
    val row: Int = 0,
    val col: Int = 0,
    @SerialName("occupant_count") val occupantCount: Double = 0.0,
    val density: Double = 0.0,
    @SerialName("alert_level") val alertLevel: String = "NORMAL",
)

internal fun RoomSnapshot.displayName(): String =
    roomId.removePrefix("device:").removePrefix("mac:").ifBlank { roomId.ifBlank { "Unknown" } }

internal fun RoomSnapshot.alertLevel(): String =
    latestPayload?.populationData?.alertLevel?.takeIf { it.isNotBlank() } ?: "NORMAL"

internal fun RoomSnapshot.currentCount(): Int =
    latestPayload?.populationData?.currentCount ?: 0

internal fun RoomSnapshot.location(): String =
    latestPayload?.deviceInfo?.location?.takeIf { it.isNotBlank() } ?: "Unknown Location"

internal fun RoomSnapshot.cameraSource(): String =
    latestPayload?.deviceInfo?.cameraSource?.takeIf { it.isNotBlank() } ?: "0"

internal fun formatDashboardTime(value: String): String {
    if (value.isBlank()) return "--:--:--"
    val timePart = value.substringAfter('T', value).take(8)
    return timePart.takeIf { it.length >= 5 } ?: value.take(8)
}

internal fun filterRooms(rooms: List<RoomSnapshot>, query: String): List<RoomSnapshot> {
    val terms = query.trim().lowercase().split(Regex("\\s+")).filter { it.isNotBlank() }
    if (terms.isEmpty()) return rooms

    return rooms.filter { room ->
        val payload = room.latestPayload
        val deviceInfo = payload?.deviceInfo
        val populationData = payload?.populationData
        val searchableText = listOfNotNull(
            room.roomId,
            room.identifierType,
            room.identifierValue,
            room.createdAt,
            room.lastSeenAt,
            room.messageCount.toString(),
            room.displayName(),
            deviceInfo?.deviceId,
            deviceInfo?.deviceName,
            deviceInfo?.location,
            deviceInfo?.cameraSource,
            deviceInfo?.macAddress,
            deviceInfo?.ipAddress,
            payload?.requestId,
            payload?.capturedAt,
            populationData?.alertLevel,
            populationData?.alertMessage,
            populationData?.currentCount?.toString(),
            populationData?.currentCount?.let { "$it occupants" },
        ).joinToString(" ").lowercase()

        terms.all { term -> searchableText.contains(term) }
    }
}
