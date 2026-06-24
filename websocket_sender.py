"""
WebSocket sender for Stampede Management.

Builds structured payloads from live tracking data and sends them to a
    Spring Boot backend with a per-device debounce interval — only the most
    recent snapshot is transmitted/logged once per interval.

Expected backend endpoint: ws://<host>:<port>/ws-raw  (plain JSON, no STOMP)
"""

import json
import socket
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING

from config import DEFAULT_WEBSOCKET_DEVICE_ID, DEFAULT_WEBSOCKET_DEVICE_NAME
from logger_config import get_logger

if TYPE_CHECKING:
    from config import MonitoringConfig, TrackData
    from occupancy import OccupancyGrid

logger = get_logger(__name__)


def get_local_mac_address() -> str:
    """Return the local machine MAC address in colon-separated format."""
    mac = uuid.getnode()
    return ":".join(f"{(mac >> shift) & 0xff:02x}" for shift in range(40, -1, -8))


try:
    import websocket as _ws_lib

    WEBSOCKET_AVAILABLE = True
except ImportError:
    _ws_lib = None
    WEBSOCKET_AVAILABLE = False
    logger.warning("websocket-client not installed — WebSocket sender disabled. "
                   "Run: pip install websocket-client")


# ─── Payload dataclasses ────────────────────────────────────────────────────

@dataclass
class BoundingBoxPayload:
    x: int
    y: int
    width: int
    height: int


@dataclass
class PersonTrackPayload:
    track_id: int
    bounding_box: BoundingBoxPayload
    confidence: float
    age: int
    confirmed: bool
    world_x: Optional[float] = None
    world_y: Optional[float] = None


@dataclass
class GridCellPayload:
    row: int
    col: int
    """Smoothed EMA occupant count (can be fractional)."""
    occupant_count: float
    """Normalised density relative to cell capacity: 0.0 – 1.0+."""
    density: float
    alert_level: str  # NORMAL | WARNING | CRITICAL


@dataclass
class OccupancyGridPayload:
    rows: int
    cols: int
    cells: List[GridCellPayload]
    total_occupants: int
    average_density: float


@dataclass
class PopulationPayload:
    current_count: int
    tracked_persons: List[PersonTrackPayload]
    occupancy_grid: OccupancyGridPayload
    alert_level: str  # NORMAL | WARNING | CRITICAL
    alert_message: Optional[str]
    frame_number: int
    fps: float


@dataclass
class DeviceInfoPayload:
    device_id: str
    device_name: str
    location: str
    camera_source: str
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class MonitoringPayload:
    """Top-level envelope sent over WebSocket."""
    device_info: DeviceInfoPayload
    population_data: PopulationPayload
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    captured_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ─── Data builder ───────────────────────────────────────────────────────────

def build_payload(
        tracks: "List[TrackData]",
        occupancy_grid: "OccupancyGrid",
        frame_count: int,
        fps_counter: list,
        fps_start_time: float,
        config: "MonitoringConfig",
) -> MonitoringPayload:
    """
    Construct a MonitoringPayload from the current monitoring state.

    Args:
        tracks:          Active TrackData objects from the tracker.
        occupancy_grid:  OccupancyGrid instance (post-update).
        frame_count:     Current frame index.
        fps_counter:     Rolling list of frame timestamps used for FPS calc.
        fps_start_time:  Session start time (unused but kept for compat).
        config:          MonitoringConfig (provides WS device meta-data).

    Returns:
        A fully populated MonitoringPayload ready for JSON serialisation.
    """
    # ── Device info ────────────────────────────────────────────────────
    device_id = config.websocket_device_id or DEFAULT_WEBSOCKET_DEVICE_ID
    mac_address = config.websocket_mac_address or get_local_mac_address()
    ip_address: Optional[str] = None
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except Exception:
        pass

    device_name = config.websocket_device_name or DEFAULT_WEBSOCKET_DEVICE_NAME
    if device_id not in device_name:
        device_name = f"{device_name} ({device_id})"

    device_info = DeviceInfoPayload(
        device_id=device_id,
        device_name=device_name,
        location=config.websocket_location,
        camera_source=str(config.source),
        mac_address=mac_address,
        ip_address=ip_address,
    )

    # ── FPS ────────────────────────────────────────────────────────────
    if len(fps_counter) > 1:
        elapsed = fps_counter[-1] - fps_counter[0]
        fps = len(fps_counter) / elapsed if elapsed > 0 else 0.0
    else:
        fps = 0.0

    # ── Tracked persons ────────────────────────────────────────────────
    tracked_persons: List[PersonTrackPayload] = []
    for t in tracks:
        x1, y1, x2, y2 = (int(v) for v in t.bbox)
        wx: Optional[float] = None
        wy: Optional[float] = None
        if t.world_position:
            wx, wy = float(t.world_position[0]), float(t.world_position[1])
        tracked_persons.append(PersonTrackPayload(
            track_id=int(t.track_id),
            bounding_box=BoundingBoxPayload(
                x=x1,
                y=y1,
                width=max(0, x2 - x1),
                height=max(0, y2 - y1),
            ),
            confidence=float(t.confidence),
            age=int(t.age),
            confirmed=bool(t.confirmed),
            world_x=wx,
            world_y=wy,
        ))

    # ── Occupancy grid cells ───────────────────────────────────────────
    warning_threshold = config.occupancy_warning_threshold  # default 0.8
    cells: List[GridCellPayload] = []
    grid_alert = "NORMAL"

    for row in range(occupancy_grid.grid_rows):
        for col in range(occupancy_grid.grid_cols):
            count = float(occupancy_grid.ema_counts[row, col])
            density = count / occupancy_grid.cell_capacity if occupancy_grid.cell_capacity else 0.0

            if count > occupancy_grid.cell_capacity:
                cell_alert = "CRITICAL"
                grid_alert = "CRITICAL"
            elif count > occupancy_grid.cell_capacity * warning_threshold:
                cell_alert = "WARNING"
                if grid_alert != "CRITICAL":
                    grid_alert = "WARNING"
            else:
                cell_alert = "NORMAL"

            cells.append(GridCellPayload(
                row=row,
                col=col,
                occupant_count=round(count, 3),
                density=round(min(density, 1.0), 3),
                alert_level=cell_alert,
            ))

    total_occupants = int(round(float(occupancy_grid.ema_counts.sum())))
    avg_density = float(
        occupancy_grid.ema_counts.mean() / occupancy_grid.cell_capacity
        if occupancy_grid.cell_capacity else 0.0
    )

    occ_grid_payload = OccupancyGridPayload(
        rows=occupancy_grid.grid_rows,
        cols=occupancy_grid.grid_cols,
        cells=cells,
        total_occupants=total_occupants,
        average_density=round(min(avg_density, 1.0), 4),
    )

    # ── Alert message ──────────────────────────────────────────────────
    alert_message: Optional[str] = None
    if grid_alert == "CRITICAL":
        alert_message = "CRITICAL: Overcapacity detected in one or more grid cells."
    elif grid_alert == "WARNING":
        alert_message = "WARNING: Crowd density approaching capacity in one or more grid cells."

    population = PopulationPayload(
        current_count=len(tracks),
        tracked_persons=tracked_persons,
        occupancy_grid=occ_grid_payload,
        alert_level=grid_alert,
        alert_message=alert_message,
        frame_number=frame_count,
        fps=round(fps, 2),
    )

    return MonitoringPayload(device_info=device_info, population_data=population)


# ─── WebSocket sender ────────────────────────────────────────────────────────

class WebSocketSender:
    """
    Sends MonitoringPayload to a WebSocket endpoint with interval debounce.

    The debounce window is per-instance (one device). The first call to
    ``schedule()`` starts the timer; calls during that window replace the
    pending payload, so the latest snapshot is transmitted/logged once the
    interval expires.

    The WebSocket connection runs in a background daemon thread and
    reconnects automatically on failure when backend requests are enabled.
    """

    def __init__(
            self,
            url: str,
            device_id: str,
            debounce_seconds: float = 3.0,
            reconnect_interval: float = 5.0,
            request_enabled: bool = False,
            log_flow: bool = True,
    ):
        self.url = url
        self.device_id = device_id
        self.debounce_seconds = debounce_seconds
        self.reconnect_interval = reconnect_interval
        self.request_enabled = request_enabled
        self.log_flow = log_flow

        self._ws = None
        self._ws_thread: Optional[threading.Thread] = None
        self._connected = False
        self._running = False

        self._timer: Optional[threading.Timer] = None
        self._timer_lock = threading.Lock()
        self._pending_payload: Optional[MonitoringPayload] = None

    # ── Connection lifecycle ─────────────────────────────────────────────

    def start(self):
        """Open the WebSocket connection in a background daemon thread."""
        self._running = True
        self._log_connection_request()

        if not self.request_enabled:
            logger.info("WebSocket backend request disabled; running in log-only mode.")
            return

        if not WEBSOCKET_AVAILABLE:
            logger.error("websocket-client is required. Install: pip install websocket-client")
            return

        self._ws_thread = threading.Thread(
            target=self._run_loop, daemon=True, name=f"ws-sender-{self.device_id}"
        )
        self._ws_thread.start()
        logger.info(f"WebSocket sender started → {self.url}")

    def stop(self):
        """Flush any pending payload and close the connection cleanly."""
        with self._timer_lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None
        self._flush(reason="shutdown")

        self._running = False
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
        logger.info("WebSocket sender stopped.")

    def _run_loop(self):
        """Background thread: maintain WebSocket connection with reconnect."""
        while self._running:
            try:
                self._ws = _ws_lib.WebSocketApp(
                    self.url,
                    on_open=self._on_open,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                self._ws.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as exc:
                logger.warning(f"WebSocket loop exception: {exc}")

            if self._running:
                logger.info(f"Reconnecting in {self.reconnect_interval}s…")
                time.sleep(self.reconnect_interval)

    def _on_open(self, ws):
        self._connected = True
        logger.info(f"WebSocket connected to {self.url}")

    def _on_error(self, ws, error):
        logger.warning(f"WebSocket error: {error}")
        self._connected = False

    def _on_close(self, ws, code, msg):
        self._connected = False
        logger.debug(f"WebSocket closed (code={code}, msg={msg})")

    # ── Debounced send ───────────────────────────────────────────────────

    def schedule(self, payload: MonitoringPayload):
        """
        Stage a payload for sending.

        Starts one debounce timer if needed; only the latest payload staged
        during that interval is sent/logged once the timer fires.
        """
        with self._timer_lock:
            self._pending_payload = payload
            if self._timer is None:
                self._timer = threading.Timer(self.debounce_seconds, self._flush)
                self._timer.daemon = True
                self._timer.start()

    def _flush(self, reason: str = "debounce"):
        """Transmit the pending payload (called by the debounce timer)."""
        with self._timer_lock:
            payload = self._pending_payload
            self._pending_payload = None
            self._timer = None

        if payload is None:
            return

        data = json.dumps(asdict(payload), default=str)
        if self.log_flow:
            self._log_payload_flow(payload, reason)

        if not self.request_enabled:
            return

        if not self._connected or self._ws is None:
            logger.warning(
                "[WS SKIP] Backend not connected | "
                f"device={payload.device_info.device_id} "
                f"request_id={payload.request_id} "
                f"frame={payload.population_data.frame_number}"
            )
            return

        try:
            self._ws.send(data)
            logger.info(
                f"[WS SENT] device={payload.device_info.device_id} "
                f"people={payload.population_data.current_count} "
                f"alert={payload.population_data.alert_level} "
                f"frame={payload.population_data.frame_number} "
                f"request_id={payload.request_id}"
            )
        except Exception as exc:
            logger.warning(f"Failed to send WebSocket message: {exc}")

    def _log_connection_request(self):
        if not self.log_flow:
            return

        logger.info(
            "[WS START] "
            f"request_enabled={self.request_enabled} "
            f"device={self.device_id} "
            f"url={self.url} "
            f"debounce_seconds={self.debounce_seconds}"
        )

    def _log_payload_flow(self, payload: MonitoringPayload, reason: str):
        logger.info(
            "[WS READY] "
            f"reason={reason} "
            f"request_enabled={self.request_enabled} "
            f"device={payload.device_info.device_id} "
            f"people={payload.population_data.current_count} "
            f"alert={payload.population_data.alert_level} "
            f"frame={payload.population_data.frame_number} "
            f"request_id={payload.request_id}"
        )
