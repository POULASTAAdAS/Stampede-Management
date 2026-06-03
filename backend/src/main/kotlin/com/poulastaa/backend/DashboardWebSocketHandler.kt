package com.poulastaa.backend

import jakarta.annotation.PostConstruct
import tools.jackson.databind.ObjectMapper
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Component
import org.springframework.web.socket.CloseStatus
import org.springframework.web.socket.TextMessage
import org.springframework.web.socket.WebSocketSession
import org.springframework.web.socket.handler.ConcurrentWebSocketSessionDecorator
import org.springframework.web.socket.handler.TextWebSocketHandler
import java.util.concurrent.ConcurrentHashMap

/**
 * WebSocket handler at /ws-dashboard.
 *
 * Browser clients connect here to:
 *  - Receive the live room list whenever it changes (type=room_list)
 *  - Subscribe to a specific room and receive its monitoring data in real time (type=room_update)
 *
 * Protocol (client → server):
 *   {"action":"subscribe",   "roomId":"device:XYZ"}
 *   {"action":"unsubscribe", "roomId":"device:XYZ"}
 *   {"action":"list"}
 *
 * Protocol (server → client):
 *   {"type":"room_list",   "rooms":[...]}
 *   {"type":"room_update", "roomId":"...", "data":{...full MonitoringPayload...}}
 *   {"type":"subscribed",  "roomId":"..."}
 *   {"type":"error",       "message":"..."}
 */
@Component
class DashboardWebSocketHandler(
    private val roomRegistry: RoomRegistry,
    private val objectMapper: ObjectMapper,
) : TextWebSocketHandler(), RoomUpdateListener {

    private val logger = LoggerFactory.getLogger(javaClass)

    // sessionId -> thread-safe session wrapper
    private val sessions = ConcurrentHashMap<String, WebSocketSession>()

    // roomId -> set of sessionIds subscribed to it
    private val subscriptions = ConcurrentHashMap<String, MutableSet<String>>()

    @PostConstruct
    fun init() {
        roomRegistry.addListener(this)
        logger.info("[DASHBOARD] Handler registered as room update listener")
    }

    // ── Connection lifecycle ─────────────────────────────────────────────────

    override fun afterConnectionEstablished(session: WebSocketSession) {
        val safe = ConcurrentWebSocketSessionDecorator(
            session,
            sendTimeLimit = 5_000,      // 5 s send timeout
            bufferSizeLimit = 256 * 1024, // 256 KB buffer
        )
        sessions[session.id] = safe
        logger.info("[DASH CONNECT] sessionId={} remoteAddress={}", session.id, session.remoteAddress)

        // Immediately push current room list to the new client
        sendToSession(safe, buildRoomListMessage())
    }

    override fun afterConnectionClosed(session: WebSocketSession, status: CloseStatus) {
        sessions.remove(session.id)
        subscriptions.values.forEach { it.remove(session.id) }
        logger.info("[DASH DISCONNECT] sessionId={} code={}", session.id, status.code)
    }

    override fun handleTransportError(session: WebSocketSession, exception: Throwable) {
        logger.warn("[DASH ERROR] sessionId={} error={}", session.id, exception.message)
    }

    // ── Message handling ─────────────────────────────────────────────────────

    override fun handleTextMessage(session: WebSocketSession, message: TextMessage) {
        val json = runCatching { objectMapper.readTree(message.payload) }.getOrNull() ?: run {
            sessions[session.id]?.let { sendToSession(it, """{"type":"error","message":"invalid_json"}""") }
            return
        }

        val safeSession = sessions[session.id] ?: return

        when (json.get("action")?.asText()) {
            "subscribe" -> {
                val roomId = json.get("roomId")?.asText()?.takeIf { it.isNotBlank() } ?: run {
                    sendToSession(safeSession, """{"type":"error","message":"missing_roomId"}""")
                    return
                }
                subscriptions.computeIfAbsent(roomId) { ConcurrentHashMap.newKeySet() }.add(session.id)
                logger.info("[DASH SUBSCRIBE] sessionId={} roomId={}", session.id, roomId)

                // Confirm subscription
                sendToSession(safeSession, objectMapper.writeValueAsString(mapOf("type" to "subscribed", "roomId" to roomId)))

                // Push last known payload immediately so the UI can show current state
                roomRegistry.getLatestPayload(roomId)?.let { payload ->
                    sendToSession(safeSession, buildRoomUpdateMessage(roomId, payload))
                }
            }

            "unsubscribe" -> {
                val roomId = json.get("roomId")?.asText() ?: return
                subscriptions[roomId]?.remove(session.id)
                logger.info("[DASH UNSUBSCRIBE] sessionId={} roomId={}", session.id, roomId)
            }

            "list" -> {
                sendToSession(safeSession, buildRoomListMessage())
            }

            else -> {
                sendToSession(safeSession, """{"type":"error","message":"unknown_action"}""")
            }
        }
    }

    // ── RoomUpdateListener ────────────────────────────────────────────────────

    override fun onRoomUpdate(room: Room, rawPayload: String) {
        // Push detail update to all sessions subscribed to this room
        val updateMsg = buildRoomUpdateMessage(room.roomId, rawPayload)
        subscriptions[room.roomId]?.forEach { sessionId ->
            sessions[sessionId]?.takeIf { it.isOpen }?.let { sendToSession(it, updateMsg) }
        }

        // Push refreshed room list to every connected session (metadata changed)
        val listMsg = buildRoomListMessage()
        sessions.values.forEach { session ->
            if (session.isOpen) sendToSession(session, listMsg)
        }
    }

    // ── Helpers ──────────────────────────────────────────────────────────────

    private fun buildRoomListMessage(): String =
        objectMapper.writeValueAsString(
            mapOf("type" to "room_list", "rooms" to roomRegistry.listRooms())
        )

    private fun buildRoomUpdateMessage(roomId: String, rawPayload: String): String {
        val dataNode = runCatching { objectMapper.readTree(rawPayload) }.getOrNull()
        return objectMapper.writeValueAsString(
            mapOf("type" to "room_update", "roomId" to roomId, "data" to dataNode)
        )
    }

    private fun sendToSession(session: WebSocketSession, message: String) {
        try {
            if (session.isOpen) {
                session.sendMessage(TextMessage(message))
            }
        } catch (e: Exception) {
            logger.warn("[DASH SEND ERROR] sessionId={} error={}", session.id, e.message)
        }
    }
}
