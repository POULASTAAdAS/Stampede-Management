import { useState, useEffect, useRef, useMemo } from 'react'
import {
  AlertTriangle, Grid, Map, Cpu, Clock, Users, Activity, Eye
} from 'lucide-react'
import './App.css'
import {
  AppContainer, DashboardBody, SidebarBackdrop, ContentArea,
  DetailHeaderPanel, MetricsRow, MetricCard, MetricIconBox, MetricValue,
  MetricName, VisualizersGrid, DetailsRow, DashboardPanel
} from './components'

// Modular Components
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import RadarScope from './components/RadarScope'
import DensityGrid from './components/DensityGrid'
import TrackedTable from './components/TrackedTable'
import ConsoleLogs from './components/ConsoleLogs'
import SettingsPanel from './components/SettingsPanel'

function App() {
  // --- States ---
  const [rooms, setRooms] = useState([])
  const [selectedRoomId, setSelectedRoomId] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isRadarSweep, setIsRadarSweep] = useState(true)
  const [isAudioMuted, setIsAudioMuted] = useState(true) // Start muted to satisfy browser policies
  const [selectedTrackId, setSelectedTrackId] = useState(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [mobileTab, setMobileTab] = useState('telemetry')
  const [isLoading, setIsLoading] = useState(true)

  // Custom limits
  const [warningThreshold, setWarningThreshold] = useState(0.7) // 70% cell density
  const [criticalThreshold, setCriticalThreshold] = useState(0.9) // 90% cell density
  const [gridRows] = useState(5)
  const [gridCols] = useState(5)

  // Historical data for Sparklines (RoomId -> List of recent occupancy counts)
  const [history, setHistory] = useState({})

  // System Log Console
  const [logs, setLogs] = useState([
    { id: 1, time: new Date().toLocaleTimeString(), msg: "Stampede Management Interface initialized", type: "system" }
  ])

  // Web socket reference
  const wsRef = useRef(null)
  const consoleLogsRef = useRef(null)

  // --- Splash Screen Timer ---
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 2200)
    return () => clearTimeout(timer)
  }, [])

  // --- Auto-scroll console ---
  useEffect(() => {
    if (consoleLogsRef.current) {
      consoleLogsRef.current.scrollTop = consoleLogsRef.current.scrollHeight
    }
  }, [logs])

  // --- WebSocket Connection ---
  useEffect(() => {
    const configuredWsUrl = import.meta.env.VITE_WS_URL
    const wsUrl = configuredWsUrl || 'wss://stamped.poulastaa.dev/ws-dashboard'

    addLog(`Attempting WebSocket connection to ${wsUrl}...`, "system")

    let active = true
    let reconnectTimeout = null

    const connectWS = () => {
      if (!active) return
      try {
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
          if (!active) {
            ws.close()
            return
          }
          setIsConnected(true)
          addLog("WebSocket Gateway Online", "system")
          // Request current room list
          ws.send(JSON.stringify({ action: "list" }))
        }

        ws.onmessage = (event) => {
          if (!active) return
          try {
            const message = JSON.parse(event.data)

            if (message.type === 'room_list') {
              setRooms(message.rooms || [])

              // Select first room if none selected
              if (message.rooms && message.rooms.length > 0 && !selectedRoomId) {
                const firstId = message.rooms[0].roomId
                setSelectedRoomId(firstId)
                // Subscribe to it
                ws.send(JSON.stringify({ action: "subscribe", roomId: firstId }))
                addLog(`Auto-subscribed to live device: ${firstId}`, "system")
              }
            }
            else if (message.type === 'room_update') {
              const { roomId, data } = message

              // Update local state for this specific room
              setRooms(prevRooms => prevRooms.map(r => {
                if (r.roomId === roomId) {
                  return {
                    ...r,
                    lastSeenAt: new Date().toISOString(),
                    latestPayload: data
                  }
                }
                return r
              }))

              // Update history trail for sparkline
              if (data && data.population_data) {
                const count = data.population_data.current_count
                setHistory(prev => {
                  const rHist = prev[roomId] || []
                  const updated = [...rHist, count].slice(-30) // Keep last 30 ticks
                  return { ...prev, [roomId]: updated }
                })

                // Audio warning trigger
                if (roomId === selectedRoomId) {
                  checkAlertLevelAndSpeak(data.population_data.alert_level, roomId)
                }
              }
            }
            else if (message.type === 'subscribed') {
              addLog(`Subscribed to telemetry stream: ${message.roomId}`, "system")
            }
            else if (message.type === 'error') {
              addLog(`Gateway Error: ${message.message}`, "error")
            }
          } catch (err) {
            console.error("Error parsing WS packet", err)
          }
        }

        ws.onclose = () => {
          setIsConnected(false)
          if (active) {
            addLog("WebSocket Connection Closed. Reconnecting in 5 seconds...", "error")
            reconnectTimeout = setTimeout(connectWS, 5000)
          }
        }

        ws.onerror = (err) => {
          console.error("WS Error", err)
          ws.close()
        }
      } catch (e) {
        console.error("WS Connection Init Error", e)
      }
    }

    connectWS()

    return () => {
      active = false
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // --- Subscribe/Unsubscribe on Room selection change ---
  const handleSelectRoom = (roomId) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Unsubscribe from previous
      if (selectedRoomId) {
        wsRef.current.send(JSON.stringify({ action: "unsubscribe", roomId: selectedRoomId }))
      }
      // Subscribe to new
      wsRef.current.send(JSON.stringify({ action: "subscribe", roomId }))
    }
    setSelectedRoomId(roomId)
    setSelectedTrackId(null)
    setIsSidebarOpen(false)
    addLog(`Navigated to monitor room: ${roomId}`, "system")
  }

  // --- Add console logs helper ---
  const addLog = (msg, type = "info") => {
    setLogs(prev => [
      ...prev,
      { id: Date.now() + Math.random(), time: new Date().toLocaleTimeString(), msg, type }
    ].slice(-50)) // Cap logs at 50 entries
  }

  // --- Audio Alert Speech Synthesis ---
  const lastAlertTimeRef = useRef({})
  const checkAlertLevelAndSpeak = (level, roomId) => {
    if (isAudioMuted || (level !== 'WARNING' && level !== 'CRITICAL')) return

    const now = Date.now()
    const lastTime = lastAlertTimeRef.current[roomId] || 0
    if (now - lastTime < 10000) return // Debounce speech to once every 10 seconds per room

    lastAlertTimeRef.current[roomId] = now
    const utterance = new SpeechSynthesisUtterance(
      level === 'CRITICAL'
        ? `Alert! Critical crowd density detected in ${roomId.replace('device:', '')}!`
        : `Warning. High density detected in ${roomId.replace('device:', '')}.`
    )
    utterance.rate = 1.0
    utterance.volume = 1.0
    window.speechSynthesis.speak(utterance)
  }

  // --- Computed Active Room details ---
  const activeRoom = useMemo(() => {
    return rooms.find(r => r.roomId === selectedRoomId) || null
  }, [rooms, selectedRoomId])

  // --- Check selected track position in overcrowded cells and play audio warning ---
  const lastGridAlertTimeRef = useRef(0)
  useEffect(() => {
    if (!activeRoom || selectedTrackId === null || isAudioMuted) return

    const payload = activeRoom.latestPayload
    if (!payload || !payload.population_data) return

    const tracks = payload.population_data.tracked_persons || []
    const selectedPerson = tracks.find(t => t.track_id === selectedTrackId)
    if (!selectedPerson) return

    // Calculate which grid cell the selected person is currently in
    const cellW = 800 / gridCols
    const cellH = 600 / gridRows
    const c = Math.floor(selectedPerson.world_x / cellW)
    const r = Math.floor(selectedPerson.world_y / cellH)

    // Bound check
    if (r < 0 || r >= gridRows || c < 0 || c >= gridCols) return

    // Find the cell data
    const cells = payload.population_data.occupancy_grid?.cells || []
    const cellData = cells.find(cell => cell.row === r && cell.col === c)
    
    // Check if overcrowded (WARNING or CRITICAL)
    if (cellData && (cellData.alert_level === 'CRITICAL' || cellData.alert_level === 'WARNING')) {
      const now = Date.now()
      if (now - lastGridAlertTimeRef.current > 8000) { // 8-second debounce
        lastGridAlertTimeRef.current = now
        
        // Play tone
        try {
          const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
          const osc1 = audioCtx.createOscillator();
          const gain1 = audioCtx.createGain();
          osc1.connect(gain1);
          gain1.connect(audioCtx.destination);
          osc1.type = 'sawtooth';
          osc1.frequency.setValueAtTime(880, audioCtx.currentTime);
          gain1.gain.setValueAtTime(0.1, audioCtx.currentTime);
          gain1.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);

          const osc2 = audioCtx.createOscillator();
          const gain2 = audioCtx.createGain();
          osc2.connect(gain2);
          gain2.connect(audioCtx.destination);
          osc2.type = 'sine';
          osc2.frequency.setValueAtTime(1100, audioCtx.currentTime);
          gain2.gain.setValueAtTime(0.1, audioCtx.currentTime);
          gain2.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);

          osc1.start();
          osc2.start();
          osc1.stop(audioCtx.currentTime + 0.4);
          osc2.stop(audioCtx.currentTime + 0.4);
        } catch (err) {
          console.warn("AudioContext tone failed", err);
        }

        // Voice alert
        try {
          const utterance = new SpeechSynthesisUtterance(
            `Warning. Selected user ${selectedTrackId} is in overcrowded grid cell, row ${r + 1}, column ${c + 1}.`
          );
          utterance.rate = 1.05;
          utterance.volume = 1.0;
          window.speechSynthesis.speak(utterance);
        } catch (err) {
          console.warn("SpeechSynthesis failed", err);
        }
        
        addLog(`WARNING: Selected user #${selectedTrackId} is in overcrowded cell [${r}, ${c}]`, "warn")
      }
    }
  }, [activeRoom, selectedTrackId, isAudioMuted, gridRows, gridCols])

  // --- Filtered Rooms (Search) ---
  const filteredRooms = useMemo(() => {
    if (!searchQuery) return rooms
    return rooms.filter(r =>
      r.roomId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.latestPayload?.device_info?.device_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.latestPayload?.device_info?.location || '').toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [rooms, searchQuery])

  // --- Render Live Population Sparkline ---
  const renderSparkline = (dataList) => {
    if (!dataList || dataList.length < 2) return null
    const width = 100
    const height = 30
    const padding = 2
    const max = Math.max(...dataList, 5)
    const min = 0
    const points = dataList.map((val, idx) => {
      const x = (idx / (dataList.length - 1)) * (width - padding * 2) + padding
      const y = height - ((val - min) / (max - min)) * (height - padding * 2) - padding
      return `${x},${y}`
    }).join(' ')

    return (
      <svg width={width} height={height} className="sparkline-chart">
        <polyline
          fill="none"
          stroke="var(--accent)"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
        <circle
          cx={(dataList.length - 1) / (dataList.length - 1) * (width - padding * 2) + padding}
          cy={height - ((dataList[dataList.length - 1] - min) / (max - min)) * (height - padding * 2) - padding}
          r="2.5"
          fill="var(--accent)"
        />
      </svg>
    )
  }

  return (
    <AppContainer>
      {/* --- Dashboard Header --- */}
      <Header
        isConnected={isConnected}
        isAudioMuted={isAudioMuted}
        setIsAudioMuted={setIsAudioMuted}
        isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
        addLog={addLog}
      />

      {/* --- Main Dashboard Body --- */}
      <DashboardBody>
        {/* --- Sidebar (Devices List) --- */}
        {isSidebarOpen && <SidebarBackdrop onClick={() => setIsSidebarOpen(false)} />}
        <Sidebar
          isOpen={isSidebarOpen}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          filteredRooms={filteredRooms}
          selectedRoomId={selectedRoomId}
          handleSelectRoom={handleSelectRoom}
          history={history}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* --- Central Telemetry Content Area --- */}
        <ContentArea>
          {!activeRoom ? (
            <div className="empty-dashboard">
              <div className="empty-radar">
                <Map size={48} className="pulse-cyan" />
              </div>
              <h2>Telemetry Console Idle</h2>
              <p>Please select a room device from the sidebar to initialize spatial heatmaps.</p>
            </div>
          ) : (
            <>
              {/* Detail Room Header */}
              <DetailHeaderPanel>
                <div className="detail-header-info">
                  <h2>{activeRoom.roomId.replace('device:', '').toUpperCase()}</h2>
                  <p>
                    <Clock size={14} />
                    <span>Live Tracking • Cam Src: <code>{activeRoom.latestPayload?.device_info?.camera_source || '0'}</code> • Refresh: 29fps</span>
                  </p>
                </div>

                {activeRoom.latestPayload?.population_data?.alert_message && (
                  <div className={`alert-banner-bar ${activeRoom.latestPayload.population_data.alert_level.toLowerCase()}`}>
                    <AlertTriangle size={16} />
                    <span>{activeRoom.latestPayload.population_data.alert_message}</span>
                  </div>
                )}
              </DetailHeaderPanel>

              {/* Metric Cards Row */}
              <MetricsRow>
                <MetricCard>
                  <MetricIconBox color="blue">
                    <Users />
                  </MetricIconBox>
                  <div className="metric-content">
                    <MetricValue>{activeRoom.latestPayload?.population_data?.current_count || 0}</MetricValue>
                    <MetricName>TOTAL CROWD COUNT</MetricName>
                  </div>
                  <div className="metric-sparkline">
                    {renderSparkline(history[activeRoom.roomId])}
                  </div>
                </MetricCard>

                <MetricCard>
                  <MetricIconBox color="cyan">
                    <Grid />
                  </MetricIconBox>
                  <div className="metric-content">
                    <MetricValue>
                      {Math.round((activeRoom.latestPayload?.population_data?.occupancy_grid?.average_density || 0) * 100)}%
                    </MetricValue>
                    <MetricName>AVG GRID DENSITY</MetricName>
                  </div>
                </MetricCard>

                <MetricCard>
                  <MetricIconBox color={activeRoom.latestPayload?.population_data?.alert_level === 'CRITICAL' ? 'red' : activeRoom.latestPayload?.population_data?.alert_level === 'WARNING' ? 'orange' : 'blue'}>
                    <AlertTriangle />
                  </MetricIconBox>
                  <div className="metric-content">
                    <MetricValue>{activeRoom.latestPayload?.population_data?.alert_level || 'NORMAL'}</MetricValue>
                    <MetricName>ROOM RISK INDEX</MetricName>
                  </div>
                </MetricCard>

                <MetricCard>
                  <MetricIconBox color="blue">
                    <Cpu />
                  </MetricIconBox>
                  <div className="metric-content">
                    <MetricValue>{activeRoom.latestPayload?.population_data?.fps || '30.0'} Hz</MetricValue>
                    <MetricName>PROCESSOR SPEED</MetricName>
                  </div>
                </MetricCard>
              </MetricsRow>

              {/* Visualizer Row */}
              <VisualizersGrid>
                {/* Visualizer 1: Live Radar Scope */}
                <RadarScope
                  isRadarSweep={isRadarSweep}
                  setIsRadarSweep={setIsRadarSweep}
                  activeRoom={activeRoom}
                  selectedTrackId={selectedTrackId}
                  setSelectedTrackId={setSelectedTrackId}
                />

                {/* Visualizer 2: Heatmap Capacity Grid */}
                <DensityGrid
                  activeRoom={activeRoom}
                  gridRows={gridRows}
                  gridCols={gridCols}
                  warningThreshold={warningThreshold}
                  criticalThreshold={criticalThreshold}
                />
              </VisualizersGrid>

              {/* Bottom Row - Data Table & Logs */}
              <DetailsRow>
                {/* Table: Tracked Persons List */}
                <TrackedTable
                  activeRoom={activeRoom}
                  selectedTrackId={selectedTrackId}
                  setSelectedTrackId={setSelectedTrackId}
                />

                {/* Panel: System Logs & Settings */}
                <DashboardPanel>
                  <ConsoleLogs logs={logs} consoleLogsRef={consoleLogsRef} />
                  <SettingsPanel
                    warningThreshold={warningThreshold}
                    setWarningThreshold={setWarningThreshold}
                    criticalThreshold={criticalThreshold}
                    setCriticalThreshold={setCriticalThreshold}
                  />
                </DashboardPanel>
              </DetailsRow>
            </>
          )}
        </ContentArea>
      </DashboardBody>

      {/* Premium Golden Splash Screen Loader */}
      <div className={`splash-overlay ${isLoading ? 'active' : 'fade-out'}`}>
        <div className="splash-content">
          <div className="splash-spinner-ring"></div>
          <div className="splash-logo">S</div>
          <h2 className="splash-title">STAMPEDE SYSTEM</h2>
          <div className="splash-bar-bg">
            <div className="splash-bar-fill"></div>
          </div>
          <p className="splash-status">ESTABLISHING CRYPTO GATEWAY LINK...</p>
        </div>
      </div>
    </AppContainer>
  )
}

export default App
