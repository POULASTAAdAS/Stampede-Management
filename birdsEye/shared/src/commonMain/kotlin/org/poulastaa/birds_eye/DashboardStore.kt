package org.poulastaa.birds_eye

import io.ktor.client.HttpClient
import io.ktor.client.plugins.websocket.DefaultClientWebSocketSession
import io.ktor.client.plugins.websocket.webSocket
import io.ktor.websocket.Frame
import io.ktor.websocket.readText
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

private const val ReconnectDelayMillis = 5_000L

class DashboardStore(
    private val wsUrl: String = DefaultDashboardWsUrl,
    private val client: HttpClient = createDashboardHttpClient(),
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private var connectionJob: Job? = null
    private var activeSession: DefaultClientWebSocketSession? = null

    private val _state = MutableStateFlow(DashboardState())
    val state: StateFlow<DashboardState> = _state

    fun start() {
        if (connectionJob?.isActive == true) return

        connectionJob = scope.launch {
            while (isActive) {
                connectOnce()
                delay(ReconnectDelayMillis)
            }
        }
    }

    fun stop() {
        connectionJob?.cancel()
        connectionJob = null
        activeSession = null
        client.close()
        _state.update { it.copy(isConnected = false) }
    }

    fun setSearchQuery(query: String) {
        _state.update { it.copy(searchQuery = query) }
    }

    fun selectRoom(roomId: String) {
        val previousRoomId = _state.value.selectedRoomId
        if (previousRoomId == roomId) return

        _state.update { it.copy(selectedRoomId = roomId, selectedTrackId = null) }

        scope.launch {
            val session = activeSession ?: return@launch
            previousRoomId?.let { session.sendAction("unsubscribe", it) }
            session.sendAction("subscribe", roomId)
        }
    }

    fun selectTrack(trackId: Int) {
        _state.update { it.copy(selectedTrackId = trackId) }
    }

    private suspend fun connectOnce() {
        try {
            client.webSocket(urlString = wsUrl) {
                activeSession = this
                _state.update { it.copy(isConnected = true, errorMessage = null) }

                sendAction("list")
                _state.value.selectedRoomId?.let { sendAction("subscribe", it) }

                try {
                    for (frame in incoming) {
                        if (frame is Frame.Text) {
                            handleServerMessage(frame.readText())
                        }
                    }
                } finally {
                    activeSession = null
                    _state.update { it.copy(isConnected = false) }
                }
            }
        } catch (exception: CancellationException) {
            throw exception
        } catch (exception: Throwable) {
            activeSession = null
            _state.update {
                it.copy(
                    isConnected = false,
                    errorMessage = exception.toDashboardErrorMessage(),
                )
            }
        }
    }

    private suspend fun handleServerMessage(text: String) {
        val element = runCatching { DashboardJson.parseToJsonElement(text).jsonObject }.getOrNull()
            ?: return

        when (element["type"]?.jsonPrimitive?.contentOrNull) {
            "room_list" -> handleRoomList(text)
            "room_update" -> handleRoomUpdate(text)
            "error" -> {
                val message = DashboardJson.decodeFromString<DashboardErrorMessage>(text)
                _state.update { it.copy(errorMessage = message.message) }
            }
        }
    }

    private suspend fun handleRoomList(text: String) {
        val message = DashboardJson.decodeFromString<RoomListMessage>(text)
        val currentSelectedRoomId = _state.value.selectedRoomId
        val roomToAutoSubscribe = if (currentSelectedRoomId == null && message.rooms.isNotEmpty()) {
            message.rooms.first().roomId
        } else {
            null
        }

        _state.update {
            it.copy(
                rooms = message.rooms,
                selectedRoomId = it.selectedRoomId ?: roomToAutoSubscribe,
                selectedTrackId = if (roomToAutoSubscribe != null) null else it.selectedTrackId,
                errorMessage = null,
            )
        }

        roomToAutoSubscribe?.let { activeSession?.sendAction("subscribe", it) }
    }

    private fun handleRoomUpdate(text: String) {
        val message = DashboardJson.decodeFromString<RoomUpdateMessage>(text)
        val count = message.data?.populationData?.currentCount

        _state.update { current ->
            val updatedRooms = current.rooms.map { room ->
                if (room.roomId == message.roomId) {
                    room.copy(latestPayload = message.data)
                } else {
                    room
                }
            }.let { rooms ->
                if (rooms.any { it.roomId == message.roomId }) {
                    rooms
                } else {
                    rooms + RoomSnapshot(roomId = message.roomId, latestPayload = message.data)
                }
            }

            val updatedHistory = if (count != null) {
                val roomHistory = (current.history[message.roomId].orEmpty() + count).takeLast(30)
                current.history + (message.roomId to roomHistory)
            } else {
                current.history
            }

            current.copy(rooms = updatedRooms, history = updatedHistory, errorMessage = null)
        }
    }

    private suspend fun DefaultClientWebSocketSession.sendAction(action: String, roomId: String? = null) {
        val payload = if (roomId == null) {
            """{"action":"$action"}"""
        } else {
            """{"action":"$action","roomId":${DashboardJson.encodeToString(roomId)}}"""
        }
        send(Frame.Text(payload))
    }
}

private fun Throwable.toDashboardErrorMessage(): String {
    val text = message?.takeIf { it.isNotBlank() } ?: return "Unable to connect to dashboard gateway"
    return when {
        "Expected HTTP 101 response" in text -> text.lineSequence().first()
        "NSURLErrorDomain" in text && "bad response" in text -> "Server rejected the WebSocket handshake."
        else -> text.lineSequence().first().take(180)
    }
}
