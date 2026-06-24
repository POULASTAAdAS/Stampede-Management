package com.poulastaa.backend

import tools.jackson.databind.JsonNode
import tools.jackson.databind.ObjectMapper
import tools.jackson.databind.node.ObjectNode
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import org.springframework.web.socket.CloseStatus
import org.springframework.web.socket.TextMessage
import org.springframework.web.socket.WebSocketSession
import org.springframework.web.socket.handler.TextWebSocketHandler

@Component
class RawMonitoringWebSocketHandler(
    private val objectMapper: ObjectMapper,
    private val roomRegistry: RoomRegistry,
) : TextWebSocketHandler() {
    private val logger = LoggerFactory.getLogger(javaClass)

    override fun afterConnectionEstablished(session: WebSocketSession) {
        logger.info(
            "[WS CONNECT] sessionId={} remoteAddress={} uri={}",
            session.id,
            session.remoteAddress,
            session.uri,
        )
    }

    override fun handleTextMessage(session: WebSocketSession, message: TextMessage) {
        val rawPayload = message.payload
        val json = runCatching { objectMapper.readTree(rawPayload) }
            .getOrElse { exception ->
                logger.warn(
                    "[WS REQUEST REJECTED] sessionId={} reason=invalid_json error={} payload={}",
                    session.id,
                    exception.message,
                    rawPayload,
                )
                session.sendMessage(TextMessage("""{"status":"rejected","reason":"invalid_json"}"""))
                return
            }

        val normalizedJson = normalizeMonitoringPayload(json)
        val normalizedPayload = objectMapper.writeValueAsString(normalizedJson)

        val identifier = extractRoomIdentifier(normalizedJson)
        if (identifier == null) {
            val requestId = normalizedJson.textAt("/request_id") ?: "unknown"
            logger.warn(
                "[WS REQUEST REJECTED] sessionId={} requestId={} reason=missing_device_id_or_mac payload={}",
                session.id,
                requestId,
                rawPayload,
            )
            session.sendMessage(TextMessage("""{"status":"rejected","reason":"missing_device_id_or_mac"}"""))
            return
        }

        val room = roomRegistry.createOrTouchRoom(identifier, normalizedPayload)
        val requestId = normalizedJson.textAt("/request_id") ?: "unknown"
        val deviceId = normalizedJson.textAt("/device_info/device_id") ?: normalizedJson.textAt("/device_id") ?: "unknown"
        val peopleCount = normalizedJson.atOrNull("/population_data/current_count")?.asInt()
        val alertLevel = normalizedJson.textAt("/population_data/alert_level") ?: "unknown"

        logger.info(
            "[WS REQUEST] sessionId={} requestId={} deviceId={} roomId={} identifierType={} identifierValue={} people={} alert={} payload={}",
            session.id,
            requestId,
            deviceId,
            room.roomId,
            room.identifierType,
            room.identifierValue,
            peopleCount,
            alertLevel,
            rawPayload,
        )

        session.sendMessage(
            TextMessage(
                objectMapper.writeValueAsString(
                    mapOf(
                        "status" to "accepted",
                        "request_id" to requestId,
                        "room_id" to room.roomId,
                    )
                )
            )
        )
    }

    override fun afterConnectionClosed(session: WebSocketSession, status: CloseStatus) {
        logger.info(
            "[WS DISCONNECT] sessionId={} code={} reason={}",
            session.id,
            status.code,
            status.reason ?: "",
        )
    }

    override fun handleTransportError(session: WebSocketSession, exception: Throwable) {
        logger.warn(
            "[WS ERROR] sessionId={} error={}",
            session.id,
            exception.message,
            exception,
        )
    }

    internal fun normalizeMonitoringPayload(json: JsonNode): JsonNode {
        val population = json.atOrNull("/population_data") as? ObjectNode ?: return json
        val cells = json.atOrNull("/population_data/occupancy_grid/cells")?.takeIf { it.isArray } ?: return json

        var gridAlert = "NORMAL"
        for (cell in cells) {
            val cellObject = cell as? ObjectNode ?: continue
            val currentAlert = cell.textAt("/alert_level")?.uppercase() ?: "NORMAL"
            val density = cell.atOrNull("/density")?.asDouble()
            val normalizedAlert = when {
                currentAlert == "CRITICAL" && density != null && density < 1.0 -> {
                    if (density >= 0.8) "WARNING" else "NORMAL"
                }
                currentAlert == "CRITICAL" -> "CRITICAL"
                currentAlert == "WARNING" -> "WARNING"
                else -> "NORMAL"
            }

            if (normalizedAlert != currentAlert) {
                cellObject.put("alert_level", normalizedAlert)
            }

            if (normalizedAlert == "CRITICAL") {
                gridAlert = "CRITICAL"
            } else if (normalizedAlert == "WARNING" && gridAlert != "CRITICAL") {
                gridAlert = "WARNING"
            }
        }

        population.put("alert_level", gridAlert)
        when (gridAlert) {
            "CRITICAL" -> population.put("alert_message", "CRITICAL: Overcapacity detected in one or more grid cells.")
            "WARNING" -> population.put("alert_message", "WARNING: Crowd density approaching capacity in one or more grid cells.")
            else -> population.putNull("alert_message")
        }

        return json
    }

    private fun extractRoomIdentifier(json: JsonNode): RoomIdentifier? {
        val deviceId = json.textAt("/device_info/device_id") ?: json.textAt("/device_id")
        if (!deviceId.isNullOrBlank()) {
            return RoomIdentifier(RoomIdentifierType.DEVICE_ID, deviceId.trim())
        }

        val macAddress = json.textAt("/device_info/mac_address") ?: json.textAt("/mac_address")
        if (!macAddress.isNullOrBlank()) {
            return RoomIdentifier(RoomIdentifierType.MAC_ADDRESS, macAddress.trim())
        }

        return null
    }

    private fun JsonNode.textAt(pointer: String): String? =
        atOrNull(pointer)?.takeIf { it.isTextual }?.asText()?.takeIf { it.isNotBlank() }

    private fun JsonNode.atOrNull(pointer: String): JsonNode? =
        at(pointer).takeUnless { it.isMissingNode || it.isNull }
}
