package org.poulastaa.birds_eye

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeContentPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.roundToInt

private val Background = Color(0xFF080B12)
private val Surface = Color(0xFF111827)
private val SurfaceRaised = Color(0xFF182235)
private val SurfaceMuted = Color(0xFF0D1320)
private val Outline = Color(0x1FFFFFFF)
private val OutlineStrong = Color(0x2EFFFFFF)
private val TextPrimary = Color(0xFFF8FAFC)
private val TextSecondary = Color(0xFFB7C2D2)
private val TextTertiary = Color(0xFF738195)
private val Primary = Color(0xFF5DD6FF)
private val PrimarySoft = Color(0x245DD6FF)
private val Success = Color(0xFF34D399)
private val Warning = Color(0xFFFBBF24)
private val Danger = Color(0xFFFB7185)

private val CardShape = RoundedCornerShape(24.dp)
private val SmallShape = RoundedCornerShape(16.dp)

@Composable
fun App(startClient: Boolean = true) {
    val store = remember { DashboardStore() }
    val state by store.state.collectAsState()

    DisposableEffect(store, startClient) {
        if (startClient) store.start()
        onDispose {
            if (startClient) store.stop()
        }
    }

    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Primary,
            background = Background,
            surface = Surface,
            surfaceVariant = SurfaceRaised,
            onPrimary = Background,
            onBackground = TextPrimary,
            onSurface = TextPrimary,
        ),
    ) {
        DashboardScreen(
            state = state,
            onSearchChange = store::setSearchQuery,
            onRoomSelected = store::selectRoom,
            onTrackSelected = store::selectTrack,
        )
    }
}

@Composable
private fun DashboardScreen(
    state: DashboardState,
    onSearchChange: (String) -> Unit,
    onRoomSelected: (String) -> Unit,
    onTrackSelected: (Int) -> Unit,
) {
    val filteredRooms = remember(state.rooms, state.searchQuery) {
        filterRooms(state.rooms, state.searchQuery)
    }
    val activeRoom = remember(state.rooms, state.selectedRoomId) {
        state.rooms.firstOrNull { it.roomId == state.selectedRoomId }
    }

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .background(Background)
            .background(
                Brush.radialGradient(
                    colors = listOf(Primary.copy(alpha = 0.12f), Color.Transparent),
                    center = Offset(120f, 40f),
                    radius = 760f,
                ),
            )
            .safeContentPadding(),
    ) {
        if (maxWidth >= 840.dp) {
            WideDashboard(
                state = state,
                filteredRooms = filteredRooms,
                activeRoom = activeRoom,
                onSearchChange = onSearchChange,
                onRoomSelected = onRoomSelected,
                onTrackSelected = onTrackSelected,
            )
        } else {
            CompactDashboard(
                state = state,
                filteredRooms = filteredRooms,
                activeRoom = activeRoom,
                onSearchChange = onSearchChange,
                onRoomSelected = onRoomSelected,
                onTrackSelected = onTrackSelected,
            )
        }
    }
}

@Composable
private fun CompactDashboard(
    state: DashboardState,
    filteredRooms: List<RoomSnapshot>,
    activeRoom: RoomSnapshot?,
    onSearchChange: (String) -> Unit,
    onRoomSelected: (String) -> Unit,
    onTrackSelected: (Int) -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 20.dp, vertical = 18.dp),
        verticalArrangement = Arrangement.spacedBy(18.dp),
    ) {
        AppHeader(state)

        if (!state.isConnected && state.errorMessage != null) {
            ConnectionWarning(state.errorMessage)
        }

        SummaryCards(state)

        if (state.rooms.isEmpty()) {
            NoRoomsState(isConnected = state.isConnected)
        } else {
            RoomPicker(
                filteredRooms = filteredRooms,
                totalRooms = state.rooms.size,
                searchQuery = state.searchQuery,
                selectedRoomId = state.selectedRoomId,
                onSearchChange = onSearchChange,
                onRoomSelected = onRoomSelected,
            )

            if (activeRoom == null) {
                SelectRoomPrompt()
            } else {
                RoomDetails(
                    room = activeRoom,
                    historyData = state.history[activeRoom.roomId].orEmpty(),
                    selectedTrackId = state.selectedTrackId,
                    onTrackSelected = onTrackSelected,
                )
            }
        }
    }
}

@Composable
private fun WideDashboard(
    state: DashboardState,
    filteredRooms: List<RoomSnapshot>,
    activeRoom: RoomSnapshot?,
    onSearchChange: (String) -> Unit,
    onRoomSelected: (String) -> Unit,
    onTrackSelected: (Int) -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(28.dp),
        verticalArrangement = Arrangement.spacedBy(24.dp),
    ) {
        AppHeader(state)

        Row(
            modifier = Modifier.fillMaxSize(),
            horizontalArrangement = Arrangement.spacedBy(24.dp),
        ) {
            Column(
                modifier = Modifier
                    .width(360.dp)
                    .fillMaxHeight()
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                SummaryCards(state)
                if (state.rooms.isEmpty()) {
                    NoRoomsState(isConnected = state.isConnected)
                } else {
                    RoomPicker(
                        filteredRooms = filteredRooms,
                        totalRooms = state.rooms.size,
                        searchQuery = state.searchQuery,
                        selectedRoomId = state.selectedRoomId,
                        onSearchChange = onSearchChange,
                        onRoomSelected = onRoomSelected,
                    )
                }
            }

            Column(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxHeight()
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(18.dp),
            ) {
                if (!state.isConnected && state.errorMessage != null) {
                    ConnectionWarning(state.errorMessage)
                }

                if (activeRoom == null) {
                    SelectRoomPrompt()
                } else {
                    RoomDetails(
                        room = activeRoom,
                        historyData = state.history[activeRoom.roomId].orEmpty(),
                        selectedTrackId = state.selectedTrackId,
                        onTrackSelected = onTrackSelected,
                    )
                }
            }
        }
    }
}

@Composable
private fun AppHeader(state: DashboardState) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .defaultMinSize(minHeight = 56.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Box(
            modifier = Modifier
                .size(46.dp)
                .clip(RoundedCornerShape(14.dp))
                .background(Brush.linearGradient(listOf(Primary, Color(0xFF2563EB)))),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = "B",
                color = TextPrimary,
                fontSize = 22.sp,
                fontWeight = FontWeight.Black,
            )
        }

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "birdsEye",
                color = TextPrimary,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Black,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = "Live crowd dashboard",
                color = TextSecondary,
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        }

        StatusBadge(
            label = if (state.isConnected) "Online" else "Offline",
            color = if (state.isConnected) Success else Warning,
        )
    }
}

@Composable
private fun SummaryCards(state: DashboardState) {
    BoxWithConstraints(modifier = Modifier.fillMaxWidth()) {
        if (maxWidth < 330.dp) {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                SummaryTile(
                    label = "Gateway",
                    value = if (state.isConnected) "Online" else "Reconnecting",
                    helper = if (state.isConnected) "Dashboard stream is connected" else "Trying again automatically",
                    color = if (state.isConnected) Success else Warning,
                    modifier = Modifier.fillMaxWidth(),
                )
                SummaryTile(
                    label = "Active rooms",
                    value = state.rooms.size.toString(),
                    helper = if (state.rooms.isEmpty()) "No devices registered" else "Tap a room below",
                    color = Primary,
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        } else {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxWidth()) {
                SummaryTile(
                    label = "Gateway",
                    value = if (state.isConnected) "Live" else "Retry",
                    helper = if (state.isConnected) "Connected" else "Auto reconnect",
                    color = if (state.isConnected) Success else Warning,
                    modifier = Modifier.weight(1f),
                )
                SummaryTile(
                    label = "Rooms",
                    value = state.rooms.size.toString(),
                    helper = if (state.rooms.isEmpty()) "No active devices" else "Monitoring now",
                    color = Primary,
                    modifier = Modifier.weight(1f),
                )
            }
        }
    }
}

@Composable
private fun SummaryTile(
    label: String,
    value: String,
    helper: String,
    color: Color,
    modifier: Modifier = Modifier,
) {
    DashboardCard(modifier = modifier.defaultMinSize(minHeight = 104.dp), padding = 16.dp) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = label,
                    color = TextSecondary,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.SemiBold,
                )
                Text(
                    text = value,
                    color = TextPrimary,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Black,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            Box(
                modifier = Modifier
                    .size(34.dp)
                    .clip(CircleShape)
                    .background(color.copy(alpha = 0.18f)),
                contentAlignment = Alignment.Center,
            ) {
                Box(Modifier.size(10.dp).clip(CircleShape).background(color))
            }
        }
        Spacer(Modifier.height(6.dp))
        Text(
            text = helper,
            color = TextTertiary,
            style = MaterialTheme.typography.bodySmall,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@Composable
private fun RoomPicker(
    filteredRooms: List<RoomSnapshot>,
    totalRooms: Int,
    searchQuery: String,
    selectedRoomId: String?,
    onSearchChange: (String) -> Unit,
    onRoomSelected: (String) -> Unit,
) {
    DashboardCard(padding = 16.dp) {
        SectionHeader(
            title = "Rooms",
            detail = if (searchQuery.isBlank()) "$totalRooms active" else "${filteredRooms.size} of $totalRooms",
        )

        Spacer(Modifier.height(12.dp))

        SearchField(searchQuery, onSearchChange)

        Spacer(Modifier.height(14.dp))

        if (filteredRooms.isEmpty()) {
            EmptyInline(
                title = "No matching rooms",
                message = "Try a different room name, location, device ID, or alert level.",
            )
        } else {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                filteredRooms.forEach { room ->
                    RoomCard(
                        room = room,
                        selected = selectedRoomId == room.roomId,
                        onClick = { onRoomSelected(room.roomId) },
                    )
                }
            }
        }
    }
}

@Composable
private fun SearchField(value: String, onValueChange: (String) -> Unit) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = Modifier
            .fillMaxWidth()
            .defaultMinSize(minHeight = 56.dp),
        singleLine = true,
        shape = RoundedCornerShape(18.dp),
        textStyle = MaterialTheme.typography.bodyLarge.copy(color = TextPrimary),
        placeholder = {
            Text(
                text = "Search rooms, cameras, locations",
                color = TextTertiary,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
        },
        colors = OutlinedTextFieldDefaults.colors(
            focusedTextColor = TextPrimary,
            unfocusedTextColor = TextPrimary,
            focusedBorderColor = Primary,
            unfocusedBorderColor = OutlineStrong,
            cursorColor = Primary,
            focusedContainerColor = SurfaceMuted,
            unfocusedContainerColor = SurfaceMuted,
        ),
    )
}

@Composable
private fun RoomCard(room: RoomSnapshot, selected: Boolean, onClick: () -> Unit) {
    val alertLevel = room.alertLevel()
    val alertColor = alertColor(alertLevel)
    val shape = RoundedCornerShape(18.dp)

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .defaultMinSize(minHeight = 96.dp)
            .clip(shape)
            .background(if (selected) PrimarySoft else SurfaceMuted)
            .border(1.dp, if (selected) Primary.copy(alpha = 0.62f) else Outline, shape)
            .clickable(onClick = onClick)
            .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Box(
            modifier = Modifier
                .width(4.dp)
                .height(58.dp)
                .clip(RoundedCornerShape(999.dp))
                .background(alertColor),
        )

        Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                text = room.primaryName(),
                color = TextPrimary,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = room.supportingLabel(),
                color = TextSecondary,
                style = MaterialTheme.typography.bodySmall,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
            Text(
                text = "Updated ${formatDashboardTime(room.lastSeenAt)}",
                color = TextTertiary,
                style = MaterialTheme.typography.labelSmall,
            )
        }

        Column(horizontalAlignment = Alignment.End, verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(
                text = room.currentCount().toString(),
                color = TextPrimary,
                fontSize = 24.sp,
                fontWeight = FontWeight.Black,
                fontFamily = FontFamily.Monospace,
            )
            AlertPill(alertLevel, alertColor)
        }
    }
}

@Composable
private fun RoomDetails(
    room: RoomSnapshot,
    historyData: List<Int>,
    selectedTrackId: Int?,
    onTrackSelected: (Int) -> Unit,
) {
    val population = room.latestPayload?.populationData
    val grid = population?.occupancyGrid ?: OccupancyGrid()
    val tracks = population?.trackedPersons.orEmpty()

    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        RoomHero(room)
        MetricGrid(
            metrics = listOf(
                MetricSpec("Occupancy", "${population?.currentCount ?: 0}", Primary, historyData),
                MetricSpec("Density", "${(grid.averageDensity * 100).roundToInt()}%", Primary, emptyList()),
                MetricSpec("Risk", population?.alertLevel ?: "Normal", alertColor(population?.alertLevel ?: "Normal"), emptyList()),
                MetricSpec("Rate", "${(population?.fps ?: 0.0).roundToInt()} Hz", Primary, emptyList()),
            ),
        )

        BoxWithConstraints(modifier = Modifier.fillMaxWidth()) {
            if (maxWidth >= 760.dp) {
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
                    RadarPanel(
                        tracks = tracks,
                        selectedTrackId = selectedTrackId,
                        onTrackSelected = onTrackSelected,
                        modifier = Modifier.weight(1.05f),
                    )
                    DensityGridPanel(grid = grid, modifier = Modifier.weight(0.95f))
                }
            } else {
                Column(verticalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
                    RadarPanel(
                        tracks = tracks,
                        selectedTrackId = selectedTrackId,
                        onTrackSelected = onTrackSelected,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    DensityGridPanel(grid = grid, modifier = Modifier.fillMaxWidth())
                }
            }
        }

        TrackedListPanel(
            tracks = tracks,
            selectedTrackId = selectedTrackId,
            onTrackSelected = onTrackSelected,
        )
    }
}

@Composable
private fun RoomHero(room: RoomSnapshot) {
    val population = room.latestPayload?.populationData
    val alertLevel = population?.alertLevel ?: "Normal"
    val alertColor = alertColor(alertLevel)

    DashboardCard(padding = 18.dp) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top,
        ) {
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(
                    text = room.primaryName(),
                    color = TextPrimary,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Black,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = room.location(),
                    color = TextSecondary,
                    style = MaterialTheme.typography.bodyMedium,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                Text(
                    text = "Camera ${room.cameraSource()} - updated ${formatDashboardTime(room.lastSeenAt)}",
                    color = TextTertiary,
                    style = MaterialTheme.typography.bodySmall,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            AlertPill(alertLevel, alertColor)
        }

        population?.alertMessage?.takeIf { it.isNotBlank() }?.let { message ->
            Spacer(Modifier.height(14.dp))
            AlertBanner(message, alertLevel)
        }
    }
}

@Composable
private fun MetricGrid(metrics: List<MetricSpec>) {
    BoxWithConstraints(modifier = Modifier.fillMaxWidth()) {
        val columns = when {
            maxWidth < 360.dp -> 1
            maxWidth < 720.dp -> 2
            else -> 4
        }

        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            metrics.chunked(columns).forEach { rowMetrics ->
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxWidth()) {
                    rowMetrics.forEach { metric ->
                        MetricCard(metric, Modifier.weight(1f))
                    }
                    repeat(columns - rowMetrics.size) {
                        Spacer(Modifier.weight(1f))
                    }
                }
            }
        }
    }
}

@Composable
private fun MetricCard(metric: MetricSpec, modifier: Modifier = Modifier) {
    DashboardCard(modifier = modifier.defaultMinSize(minHeight = 98.dp), padding = 14.dp) {
        Text(
            text = metric.label,
            color = TextSecondary,
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.SemiBold,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
        Spacer(Modifier.height(8.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = metric.value,
                color = TextPrimary,
                fontSize = 24.sp,
                fontWeight = FontWeight.Black,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .clip(CircleShape)
                    .background(metric.color.copy(alpha = 0.16f)),
                contentAlignment = Alignment.Center,
            ) {
                Box(Modifier.size(9.dp).clip(CircleShape).background(metric.color))
            }
        }
        if (metric.history.size >= 2) {
            Spacer(Modifier.height(10.dp))
            Sparkline(metric.history, Modifier.fillMaxWidth().height(24.dp))
        }
    }
}

@Composable
private fun RadarPanel(
    tracks: List<PersonTrack>,
    selectedTrackId: Int?,
    onTrackSelected: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    Panel(
        title = "Position map",
        detail = if (tracks.isEmpty()) "No tracked occupants" else "${tracks.size} tracked",
        modifier = modifier,
    ) {
        val selectedTrack = tracks.firstOrNull { it.trackId == selectedTrackId }

        BoxWithConstraints(
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(min = 250.dp)
                .aspectRatio(1.24f)
                .clip(RoundedCornerShape(20.dp))
                .background(SurfaceMuted)
                .border(1.dp, Outline, RoundedCornerShape(20.dp)),
        ) {
            Canvas(Modifier.fillMaxSize()) {
                val gridColor = Color.White.copy(alpha = 0.055f)
                val center = Offset(size.width / 2f, size.height / 2f)
                for (index in 1 until 6) {
                    val x = size.width * index / 6f
                    drawLine(gridColor, Offset(x, 0f), Offset(x, size.height), strokeWidth = 1f)
                }
                for (index in 1 until 5) {
                    val y = size.height * index / 5f
                    drawLine(gridColor, Offset(0f, y), Offset(size.width, y), strokeWidth = 1f)
                }
                listOf(0.22f, 0.38f, 0.52f).forEach { radius ->
                    drawCircle(Primary.copy(alpha = 0.13f), size.minDimension * radius, center, style = Stroke(width = 1.3f))
                }
                drawCircle(Primary.copy(alpha = 0.24f), 4.5f, center)
            }

            tracks.forEach { track ->
                val x = (track.worldX ?: return@forEach).coerceIn(0.0, 800.0) / 800.0
                val y = (track.worldY ?: return@forEach).coerceIn(0.0, 600.0) / 600.0
                val selected = track.trackId == selectedTrackId
                val dotColor = if (selected) Primary else if (track.confirmed) Success else Warning
                Box(
                    modifier = Modifier
                        .offset(x = maxWidth * x.toFloat() - 18.dp, y = maxHeight * y.toFloat() - 18.dp)
                        .size(36.dp)
                        .clip(CircleShape)
                        .background(dotColor.copy(alpha = if (selected) 0.26f else 0.16f))
                        .border(1.dp, dotColor.copy(alpha = 0.78f), CircleShape)
                        .clickable { onTrackSelected(track.trackId) },
                    contentAlignment = Alignment.Center,
                ) {
                    Box(Modifier.size(if (selected) 12.dp else 9.dp).clip(CircleShape).background(dotColor))
                }
            }

            if (tracks.isEmpty()) {
                EmptyOverlay(
                    title = "No positions yet",
                    message = "Tracked people will appear here when a room sends coordinates.",
                    modifier = Modifier.align(Alignment.Center).padding(24.dp),
                )
            }

            if (selectedTrack != null) {
                RadarHud(selectedTrack, Modifier.align(Alignment.BottomStart).padding(12.dp))
            }
        }
    }
}

@Composable
private fun DensityGridPanel(grid: OccupancyGrid, modifier: Modifier = Modifier) {
    val rows = grid.rows.takeIf { it > 0 } ?: 5
    val cols = grid.cols.takeIf { it > 0 } ?: 5
    val cellsByPosition = remember(grid.cells) { grid.cells.associateBy { it.row to it.col } }

    Panel(
        title = "Density grid",
        detail = "${grid.totalOccupants} occupants",
        modifier = modifier,
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .widthIn(max = (cols * 58).dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(SurfaceMuted)
                    .border(1.dp, Outline, RoundedCornerShape(18.dp))
                    .padding(6.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                repeat(rows) { row ->
                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier.fillMaxWidth()) {
                        repeat(cols) { col ->
                            val cell = cellsByPosition[row to col] ?: GridCell(row = row, col = col)
                            DensityCell(cell, Modifier.weight(1f))
                        }
                    }
                }
            }

            Row(
                modifier = Modifier.horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                LegendItem("Normal", Success)
                LegendItem("Warning", Warning)
                LegendItem("Critical", Danger)
            }
        }
    }
}

@Composable
private fun TrackedListPanel(
    tracks: List<PersonTrack>,
    selectedTrackId: Int?,
    onTrackSelected: (Int) -> Unit,
) {
    Panel(
        title = "Tracked people",
        detail = if (tracks.isEmpty()) "None" else tracks.size.toString(),
        modifier = Modifier.fillMaxWidth(),
    ) {
        if (tracks.isEmpty()) {
            EmptyInline(
                title = "No tracked people",
                message = "People will appear here when the active detector reports tracks.",
            )
        } else {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                tracks.forEach { track ->
                    TrackRow(
                        track = track,
                        selected = track.trackId == selectedTrackId,
                        onClick = { onTrackSelected(track.trackId) },
                    )
                }
            }
        }
    }
}

@Composable
private fun TrackRow(track: PersonTrack, selected: Boolean, onClick: () -> Unit) {
    val confidencePercent = (track.confidence * 100).roundToInt().coerceIn(0, 100)
    val confidenceColor = when {
        confidencePercent < 50 -> Danger
        confidencePercent < 75 -> Warning
        else -> Success
    }
    val shape = RoundedCornerShape(18.dp)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .defaultMinSize(minHeight = 78.dp)
            .clip(shape)
            .background(if (selected) PrimarySoft else SurfaceMuted)
            .border(1.dp, if (selected) Primary.copy(alpha = 0.62f) else Outline, shape)
            .clickable(onClick = onClick)
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Text(
                text = "Track #${track.trackId}",
                color = TextPrimary,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
            )
            StatusText(if (track.confirmed) "Confirmed" else "Pending", if (track.confirmed) Success else Warning)
        }
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Box(
                modifier = Modifier
                    .weight(1f)
                    .height(8.dp)
                    .clip(RoundedCornerShape(999.dp))
                    .background(Color.White.copy(alpha = 0.08f)),
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(confidencePercent / 100f)
                        .fillMaxHeight()
                        .background(confidenceColor),
                )
            }
            Text(
                text = "$confidencePercent%",
                color = confidenceColor,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
            )
        }
        Text(
            text = "Age ${track.age} frames - ${track.worldX?.roundToInt() ?: 0}, ${track.worldY?.roundToInt() ?: 0}",
            color = TextTertiary,
            style = MaterialTheme.typography.bodySmall,
        )
    }
}

@Composable
private fun NoRoomsState(isConnected: Boolean) {
    DashboardCard(padding = 22.dp) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Box(
                modifier = Modifier
                    .size(64.dp)
                    .clip(CircleShape)
                    .background(PrimarySoft),
                contentAlignment = Alignment.Center,
            ) {
                Canvas(Modifier.size(38.dp)) {
                    drawCircle(Primary.copy(alpha = 0.22f), radius = size.minDimension * 0.48f, style = Stroke(width = 2f))
                    drawCircle(Primary, radius = 4.8f, center = center)
                    drawLine(
                        Primary.copy(alpha = 0.75f),
                        center,
                        Offset(size.width * 0.78f, size.height * 0.28f),
                        strokeWidth = 2.5f,
                        cap = StrokeCap.Round,
                    )
                }
            }
            Text(
                text = "No active rooms",
                color = TextPrimary,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Black,
                textAlign = TextAlign.Center,
            )
            Text(
                text = "Start a detection client. Rooms will appear automatically when the dashboard stream receives data.",
                color = TextSecondary,
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
                lineHeight = 20.sp,
            )
            StatusBadge(
                label = if (isConnected) "Gateway connected" else "Waiting for gateway",
                color = if (isConnected) Success else Warning,
            )
        }
    }
}

@Composable
private fun SelectRoomPrompt() {
    DashboardCard(padding = 22.dp) {
        EmptyOverlay(
            title = "Choose a room",
            message = "Select a room to view occupancy, density, and tracked people.",
            modifier = Modifier.fillMaxWidth(),
        )
    }
}

@Composable
private fun ConnectionWarning(message: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(18.dp))
            .background(Warning.copy(alpha = 0.12f))
            .border(1.dp, Warning.copy(alpha = 0.26f), RoundedCornerShape(18.dp))
            .padding(14.dp),
        verticalAlignment = Alignment.Top,
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Box(Modifier.size(10.dp).clip(CircleShape).background(Warning).padding(top = 4.dp))
        Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Text(
                text = "Reconnecting to gateway",
                color = Warning,
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = message,
                color = TextSecondary,
                style = MaterialTheme.typography.bodySmall,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis,
            )
        }
    }
}

@Composable
private fun Panel(
    title: String,
    detail: String,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    DashboardCard(modifier = modifier, padding = 16.dp) {
        SectionHeader(title, detail)
        Spacer(Modifier.height(14.dp))
        content()
    }
}

@Composable
private fun DashboardCard(
    modifier: Modifier = Modifier,
    padding: Dp = 18.dp,
    content: @Composable () -> Unit,
) {
    Column(
        modifier = modifier
            .clip(CardShape)
            .background(Brush.verticalGradient(listOf(SurfaceRaised.copy(alpha = 0.96f), Surface.copy(alpha = 0.96f))))
            .border(1.dp, Outline, CardShape)
            .padding(padding),
    ) {
        content()
    }
}

@Composable
private fun SectionHeader(title: String, detail: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = title,
            color = TextPrimary,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.weight(1f),
        )
        Text(
            text = detail,
            color = TextTertiary,
            style = MaterialTheme.typography.labelMedium,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@Composable
private fun AlertBanner(message: String, level: String) {
    val color = alertColor(level)
    Text(
        text = message,
        color = color,
        style = MaterialTheme.typography.bodyMedium,
        fontWeight = FontWeight.SemiBold,
        modifier = Modifier
            .fillMaxWidth()
            .clip(SmallShape)
            .background(color.copy(alpha = 0.12f))
            .border(1.dp, color.copy(alpha = 0.24f), SmallShape)
            .padding(12.dp),
    )
}

@Composable
private fun AlertPill(level: String, color: Color) {
    Text(
        text = level.uppercase(),
        color = color,
        style = MaterialTheme.typography.labelSmall,
        fontWeight = FontWeight.Black,
        maxLines = 1,
        modifier = Modifier
            .clip(RoundedCornerShape(999.dp))
            .background(color.copy(alpha = 0.13f))
            .padding(horizontal = 9.dp, vertical = 5.dp),
    )
}

@Composable
private fun StatusBadge(label: String, color: Color) {
    Row(
        modifier = Modifier
            .defaultMinSize(minHeight = 40.dp)
            .clip(RoundedCornerShape(999.dp))
            .background(color.copy(alpha = 0.13f))
            .border(1.dp, color.copy(alpha = 0.26f), RoundedCornerShape(999.dp))
            .padding(horizontal = 12.dp, vertical = 9.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(Modifier.size(8.dp).clip(CircleShape).background(color))
        Text(
            text = label,
            color = color,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = FontWeight.Bold,
            maxLines = 1,
        )
    }
}

@Composable
private fun StatusText(label: String, color: Color) {
    Text(
        text = label,
        color = color,
        style = MaterialTheme.typography.labelSmall,
        fontWeight = FontWeight.Bold,
        modifier = Modifier
            .clip(RoundedCornerShape(999.dp))
            .background(color.copy(alpha = 0.12f))
            .padding(horizontal = 8.dp, vertical = 4.dp),
    )
}

@Composable
private fun DensityCell(cell: GridCell, modifier: Modifier = Modifier) {
    val density = cell.density.coerceIn(0.0, 1.0).toFloat()
    val color = alertColor(cell.alertLevel)
    Box(
        modifier = modifier
            .aspectRatio(1f)
            .clip(RoundedCornerShape(12.dp))
            .background(color.copy(alpha = 0.07f + density * 0.30f))
            .border(1.dp, color.copy(alpha = 0.20f), RoundedCornerShape(12.dp)),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = cell.occupantCount.roundToInt().toString(),
            color = color,
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.Black,
            fontFamily = FontFamily.Monospace,
        )
    }
}

@Composable
private fun RadarHud(track: PersonTrack, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .widthIn(max = 250.dp)
            .clip(RoundedCornerShape(18.dp))
            .background(Background.copy(alpha = 0.92f))
            .border(1.dp, Primary.copy(alpha = 0.30f), RoundedCornerShape(18.dp))
            .padding(12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Text("Track #${track.trackId}", color = Primary, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
            Text(if (track.confirmed) "Confirmed" else "Pending", color = if (track.confirmed) Success else Warning, style = MaterialTheme.typography.labelSmall)
        }
        HudLine("Confidence", "${(track.confidence * 100).roundToInt()}%")
        HudLine("Age", "${track.age} frames")
        HudLine("Position", "${track.worldX?.roundToInt() ?: 0}, ${track.worldY?.roundToInt() ?: 0}")
    }
}

@Composable
private fun HudLine(label: String, value: String) {
    Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
        Text(label, color = TextTertiary, style = MaterialTheme.typography.labelSmall)
        Text(value, color = TextPrimary, style = MaterialTheme.typography.labelSmall, fontFamily = FontFamily.Monospace)
    }
}

@Composable
private fun LegendItem(label: String, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        Box(Modifier.size(10.dp).clip(CircleShape).background(color.copy(alpha = 0.22f)).border(1.dp, color, CircleShape))
        Text(label, color = TextSecondary, style = MaterialTheme.typography.labelSmall)
    }
}

@Composable
private fun EmptyInline(title: String, message: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(18.dp))
            .background(SurfaceMuted)
            .border(1.dp, Outline, RoundedCornerShape(18.dp))
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(title, color = TextPrimary, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
        Text(message, color = TextTertiary, style = MaterialTheme.typography.bodySmall, lineHeight = 18.sp)
    }
}

@Composable
private fun EmptyOverlay(title: String, message: String, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text(
            text = title,
            color = TextPrimary,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
        )
        Text(
            text = message,
            color = TextSecondary,
            style = MaterialTheme.typography.bodySmall,
            textAlign = TextAlign.Center,
            lineHeight = 18.sp,
        )
    }
}

@Composable
private fun Sparkline(data: List<Int>, modifier: Modifier = Modifier) {
    if (data.size < 2) {
        Spacer(modifier)
        return
    }

    Canvas(modifier) {
        val maxValue = maxOf(data.maxOrNull() ?: 1, 1).toFloat()
        val path = Path()
        data.forEachIndexed { index, value ->
            val x = if (data.lastIndex == 0) 0f else index / data.lastIndex.toFloat() * size.width
            val y = size.height - (value / maxValue) * (size.height - 4f) - 2f
            if (index == 0) path.moveTo(x, y) else path.lineTo(x, y)
        }
        drawPath(path, Primary, style = Stroke(width = 2.2f, cap = StrokeCap.Round))
        val latestY = size.height - (data.last() / maxValue) * (size.height - 4f) - 2f
        drawCircle(Primary, radius = 4.2f, center = Offset(size.width, latestY))
    }
}

private fun alertColor(level: String): Color = when (level.uppercase()) {
    "CRITICAL" -> Danger
    "WARNING" -> Warning
    else -> Success
}

private fun RoomSnapshot.primaryName(): String =
    latestPayload?.deviceInfo?.deviceName?.takeIf { it.isNotBlank() } ?: displayName()

private fun RoomSnapshot.supportingLabel(): String {
    val location = location()
    val camera = cameraSource()
    return if (location == "Unknown Location") {
        "Camera $camera"
    } else {
        "$location - Camera $camera"
    }
}

private data class MetricSpec(
    val label: String,
    val value: String,
    val color: Color,
    val history: List<Int>,
)
