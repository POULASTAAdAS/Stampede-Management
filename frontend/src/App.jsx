import { useState, useEffect, useRef, useMemo } from 'react'
import {
  Activity, AlertTriangle,
  Volume2, VolumeX, Terminal, Users,
  Search, Grid, Map, Cpu,
  Clock, Video, RefreshCw, Menu, X
} from 'lucide-react'
import './App.css'
import {
  AppContainer, Header, BrandSection, SidebarToggle, BrandLogo, BrandText,
  HeaderControls, SystemStatus, StatusIndicator, StatusLabel, ToggleDemoBtn,
  IconOnlyBtn, DashboardBody, SidebarBackdrop, Sidebar, SidebarSearchWrap,
  SearchContainer, SidebarTitle, RoomsList, RoomCard, ContentArea,
  DetailHeaderPanel, MetricsRow, MetricCard, MetricIconBox, MetricValue,
  MetricName, VisualizersGrid, DetailsRow, DashboardPanel, RadarContainerOuter,
  RadarSweepBeam, GridWrapper, GridCellBox, LogConsole
} from './components'

function App() {
  // --- States ---
  const [rooms, setRooms] = useState([])
  const [selectedRoomId, setSelectedRoomId] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isSimulated, setIsSimulated] = useState(true) // Defaults to true so it works immediately
  const [isRadarSweep, setIsRadarSweep] = useState(true)
  const [isAudioMuted, setIsAudioMuted] = useState(true) // Start muted to satisfy browser policies
  const [selectedTrackId, setSelectedTrackId] = useState(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // Custom limits
  const [warningThreshold, setWarningThreshold] = useState(0.7) // 70% cell density
  const [criticalThreshold, setCriticalThreshold] = useState(0.9) // 90% cell density
  const [gridRows] = useState(5)
  const [gridCols] = useState(5)

  // Historical data for Sparklines (RoomId -> List of recent occupancy counts)
  const [history, setHistory] = useState({})

  // System Log Console
  const [logs, setLogs] = useState([
    { id: 1, time: new Date().toLocaleTimeString(), msg: "Stampede Management Interface initialized", type: "system" },
    { id: 2, time: new Date().toLocaleTimeString(), msg: "Interactive Simulated Demo mode active by default", type: "system" }
  ])

  // Web socket reference
  const wsRef = useRef(null)
  const simulatedTimerRef = useRef(null)
  const consoleEndRef = useRef(null)

  // --- Auto-scroll console ---
  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs])

  // --- WebSocket Connection ---
  useEffect(() => {
    if (isSimulated) {
      if (wsRef.current) {
        wsRef.current.close()
      }
      return
    }

    const configuredWsUrl = import.meta.env.VITE_WS_URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.hostname || 'localhost'
    const wsHost = host === 'localhost' || host === '127.0.0.1'
      ? `${host}:9990`
      : window.location.host
    const wsUrl = configuredWsUrl || `${protocol}//${wsHost}/ws-dashboard`

    addLog(`Attempting WebSocket connection to ${wsUrl}...`, "system")

    const connectWS = () => {
      try {
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
          setIsConnected(true)
          addLog("WebSocket Gateway Online", "system")
          // Request current room list
          ws.send(JSON.stringify({ action: "list" }))
        }

        ws.onmessage = (event) => {
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
                  const updated = [...rHist, count].slice(-20) // Keep last 20 ticks
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
          addLog("WebSocket Connection Closed. Gateway Offline.", "error")
          // If we disconnected automatically, switch to simulated to keep the UI interactive
          setIsSimulated(true)
          addLog("Switched back to Simulated Demo Mode automatically", "system")
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
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
    // Reconnect only when switching between simulator and live backend modes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSimulated])

  // --- Subscribe/Unsubscribe on Room selection change ---
  const handleSelectRoom = (roomId) => {
    if (!isSimulated && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
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

  // --- Simulated Data Engine ---
  useEffect(() => {
    if (!isSimulated) {
      if (simulatedTimerRef.current) {
        clearInterval(simulatedTimerRef.current)
      }
      return
    }

    // Initialize mock rooms
    const mockRoomTemplates = [
      { roomId: 'device:main-hallway-north', name: 'Main Hallway North', location: 'Section A1', cam: 'Webcam #1' },
      { roomId: 'device:gate-2-east-entry', name: 'Gate 2 East Entry', location: 'Gate 2', cam: 'IP-Cam #4' },
      { roomId: 'device:zone-c-escalator', name: 'Zone C Escalator', location: 'Zone C', cam: 'HD-DOME #2' }
    ]

    // Initialize mock tracks state
    const mockTracks = {}
    mockRoomTemplates.forEach(r => {
      mockTracks[r.roomId] = Array.from({ length: 8 }, (_, i) => createMockPerson(i + 1))
    })

    // Demo mode needs to seed mock room state when the simulator starts.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setRooms(mockRoomTemplates.map(r => ({
      roomId: r.roomId,
      identifierType: 'DEVICE_ID',
      identifierValue: r.roomId.replace('device:', ''),
      createdAt: new Date().toISOString(),
      lastSeenAt: new Date().toISOString(),
      messageCount: 1,
      latestPayload: generateMockPayload(r.roomId, r.name, r.location, r.cam, mockTracks[r.roomId])
    })))

    if (!selectedRoomId) {
      setSelectedRoomId(mockRoomTemplates[0].roomId)
    }

    // Tick updates every 1.2 seconds
    simulatedTimerRef.current = setInterval(() => {
      setRooms(prevRooms => {
        return prevRooms.map(r => {
          // Walk people around
          let tracks = mockTracks[r.roomId] || []

          // Randomly add, remove, or modify tracks
          if (Math.random() < 0.15 && tracks.length < 25) {
            tracks.push(createMockPerson(tracks.length > 0 ? Math.max(...tracks.map(t => t.track_id)) + 1 : 1))
          }
          if (Math.random() < 0.12 && tracks.length > 2) {
            const index = Math.floor(Math.random() * tracks.length)
            tracks.splice(index, 1)
          }

          tracks = tracks.map(t => {
            const stepSize = 15
            let dx = (Math.random() - 0.5) * stepSize
            let dy = (Math.random() - 0.5) * stepSize

            // Boundary bouncing (relative to 800x600 grid space)
            let newX = t.world_x + dx
            let newY = t.world_y + dy
            if (newX < 20 || newX > 780) dx = -dx
            if (newY < 20 || newY > 580) dy = -dy

            return {
              ...t,
              world_x: Math.max(20, Math.min(780, t.world_x + dx)),
              world_y: Math.max(20, Math.min(580, t.world_y + dy)),
              bounding_box: {
                x: Math.round(t.world_x - 15),
                y: Math.round(t.world_y - 40),
                width: 30,
                height: 80
              },
              age: t.age + 1
            }
          })

          mockTracks[r.roomId] = tracks

          const payload = generateMockPayload(r.roomId, r.identifierValue, r.roomId.replace('device:', 'Zone '), '0', tracks)

          // Add history for sparklines
          setHistory(prev => {
            const rHist = prev[r.roomId] || []
            const updated = [...rHist, tracks.length].slice(-20)
            return { ...prev, [r.roomId]: updated }
          })

          // Speak alerts if needed
          if (r.roomId === selectedRoomId) {
            checkAlertLevelAndSpeak(payload.population_data.alert_level, r.roomId)
            if (payload.population_data.alert_level === 'CRITICAL') {
              if (Math.random() < 0.25) {
                addLog(`CRITICAL: Overcapacity detected in ${r.roomId.replace('device:', '')}`, "error")
              }
            } else if (payload.population_data.alert_level === 'WARNING') {
              if (Math.random() < 0.15) {
                addLog(`WARNING: High density in ${r.roomId.replace('device:', '')}`, "warn")
              }
            }
          }

          return {
            ...r,
            lastSeenAt: new Date().toISOString(),
            messageCount: r.messageCount + 1,
            latestPayload: payload
          }
        })
      })
    }, 1200)

    return () => {
      clearInterval(simulatedTimerRef.current)
    }
    // Simulator callbacks intentionally close over the selected room and thresholds for each run.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSimulated, selectedRoomId, gridRows, gridCols, warningThreshold, criticalThreshold, isAudioMuted])

  // --- Helper to spawn a mock person coordinates ---
  function createMockPerson(id) {
    return {
      track_id: id,
      bounding_box: { x: 0, y: 0, width: 0, height: 0 },
      confidence: parseFloat((0.75 + Math.random() * 0.22).toFixed(2)),
      age: Math.floor(Math.random() * 100) + 1,
      confirmed: Math.random() > 0.1,
      world_x: Math.random() * 700 + 50,
      world_y: Math.random() * 500 + 50
    }
  }

  // --- Helper to build JSON mock telemetry packet ---
  function generateMockPayload(roomId, name, location, cam, tracks) {
    // Occupancy Grid calculations
    const cellCapacity = 2.5
    const cells = []

    // Fill empty grid cells
    for (let r = 0; r < gridRows; r++) {
      for (let c = 0; c < gridCols; c++) {
        // Count how many tracks fall inside this cell's coordinate bounds
        // Grid space width: 800, height: 600
        const cellW = 800 / gridCols
        const cellH = 600 / gridRows
        const minX = c * cellW
        const maxX = minX + cellW
        const minY = r * cellH
        const maxY = minY + cellH

        const occupants = tracks.filter(t => t.world_x >= minX && t.world_x < maxX && t.world_y >= minY && t.world_y < maxY).length
        const density = occupants / cellCapacity

        let cellAlert = 'NORMAL'
        if (density >= criticalThreshold) cellAlert = 'CRITICAL'
        else if (density >= warningThreshold) cellAlert = 'WARNING'

        cells.push({
          row: r,
          col: c,
          occupant_count: occupants,
          density: parseFloat(density.toFixed(2)),
          alert_level: cellAlert
        })
      }
    }

    // Overall alert level is maximum of cell alerts
    let gridAlert = 'NORMAL'
    if (cells.some(c => c.alert_level === 'CRITICAL')) gridAlert = 'CRITICAL'
    else if (cells.some(c => c.alert_level === 'WARNING')) gridAlert = 'WARNING'

    return {
      device_info: {
        device_id: roomId,
        device_name: name,
        location: location,
        camera_source: cam,
        mac_address: '4A:D2:7C:9B:F3:11',
        ip_address: '192.168.1.145',
        timestamp: new Date().toISOString()
      },
      population_data: {
        current_count: tracks.length,
        tracked_persons: tracks,
        occupancy_grid: {
          rows: gridRows,
          cols: gridCols,
          cells: cells,
          total_occupants: tracks.length,
          average_density: parseFloat((cells.reduce((sum, c) => sum + c.density, 0) / cells.length).toFixed(3))
        },
        alert_level: gridAlert,
        alert_message: gridAlert === 'CRITICAL' ? 'CRITICAL: Overcapacity detected!' : gridAlert === 'WARNING' ? 'WARNING: High occupancy detected' : null,
        frame_number: Math.floor(Date.now() / 1000) % 50000,
        fps: 29.8
      },
      request_id: Math.random().toString(36).substring(7),
      captured_at: new Date().toISOString()
    }
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

  // Render glowing line charts for history
  const renderSparkline = (roomId) => {
    const data = history[roomId] || []
    if (data.length < 2) return null

    const maxVal = Math.max(...data, 5)
    const width = 120
    const height = 36
    const points = data.map((val, idx) => {
      const x = (idx / (data.length - 1)) * width
      const y = height - (val / maxVal) * (height - 4) - 2
      return `${x},${y}`
    }).join(' ')

    return (
      <div className="mini-chart-container">
        <svg className="mini-chart-svg">
          <polyline
            fill="none"
            stroke="var(--accent)"
            strokeWidth="1.5"
            points={points}
          />
          <circle
            cx={width}
            cy={height - (data[data.length - 1] / maxVal) * (height - 4) - 2}
            r="3"
            fill="var(--accent)"
            className="pulse-cyan"
          />
        </svg>
      </div>
    )
  }

  // Generate trigger functions for mock simulation triggers
  const triggerMockCongestion = () => {
    if (!isSimulated || !activeRoom) return
    addLog(`Manually injecting crowd surge into ${activeRoom.roomId.replace('device:', '')}`, "warn")

    // Spawn 15-20 people packed close together at the center
    setRooms(prevRooms => prevRooms.map(r => {
      if (r.roomId === selectedRoomId) {
        const payload = r.latestPayload
        if (!payload) return r
        const currentTracks = [...(payload.population_data?.tracked_persons || [])]

        // Spawn congested coordinates
        const surgePeople = Array.from({ length: 14 }, (_, i) => {
          const id = currentTracks.length > 0 ? Math.max(...currentTracks.map(t => t.track_id)) + 1 + i : 1 + i
          return {
            track_id: id,
            bounding_box: { x: 0, y: 0, width: 0, height: 0 },
            confidence: 0.99,
            age: 1,
            confirmed: true,
            world_x: 400 + (Math.random() - 0.5) * 80, // Centralized
            world_y: 300 + (Math.random() - 0.5) * 80
          }
        })

        const newTracks = [...currentTracks, ...surgePeople]
        return {
          ...r,
          latestPayload: generateMockPayload(r.roomId, r.identifierValue, r.roomId.replace('device:', 'Zone '), '0', newTracks)
        }
      }
      return r
    }))
  }

  const triggerClearCrowd = () => {
    if (!isSimulated || !activeRoom) return
    addLog(`Clearing simulated congestion for ${activeRoom.roomId.replace('device:', '')}`, "system")
    setRooms(prevRooms => prevRooms.map(r => {
      if (r.roomId === selectedRoomId) {
        // Drop down to 2 people
        const payload = r.latestPayload
        if (!payload) return r
        const newTracks = Array.from({ length: 2 }, (_, i) => createMockPerson(i + 1))
        return {
          ...r,
          latestPayload: generateMockPayload(r.roomId, r.identifierValue, r.roomId.replace('device:', 'Zone '), '0', newTracks)
        }
      }
      return r
    }))
  }

  return (
    <AppContainer>
      {/* --- Dashboard Header --- */}
      <Header>
        <BrandSection>
          <SidebarToggle 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            aria-label="Toggle Sidebar"
          >
            {isSidebarOpen ? <X size={18} /> : <Menu size={18} />}
          </SidebarToggle>
          <BrandLogo>
            <Activity size={18} color="#fff" />
          </BrandLogo>
          <BrandText>
            <h1>Stampede Defense</h1>
            <span>Live Telemetry v2.0</span>
          </BrandText>
        </BrandSection>

        {/* Global Stats */}
        <HeaderControls>
          <SystemStatus>
            <StatusIndicator state={isSimulated ? 'simulated' : isConnected ? 'online' : 'offline'} />
            <StatusLabel>
              GATEWAY: <strong>{isSimulated ? 'SIMULATOR' : isConnected ? 'CONNECTED' : 'OFFLINE'}</strong>
            </StatusLabel>
          </SystemStatus>

          <ToggleDemoBtn
            active={isSimulated}
            onClick={() => {
              setIsSimulated(!isSimulated)
              addLog(isSimulated ? "Reconnecting to Spring Boot backend..." : "Enabled offline demo mode", "system")
            }}
          >
            {isSimulated ? 'RUN SPRING BACKEND' : 'SIMULATE OFFLINE'}
          </ToggleDemoBtn>

          <IconOnlyBtn
            active={!isAudioMuted}
            onClick={() => {
              setIsAudioMuted(!isAudioMuted)
              addLog(!isAudioMuted ? "Audio alerts enabled" : "Audio warnings muted", "system")
            }}
            title={isAudioMuted ? "Unmute Voice Alerter" : "Mute Voice Alerter"}
          >
            {isAudioMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
          </IconOnlyBtn>
        </HeaderControls>
      </Header>

      {/* --- Main Dashboard Body --- */}
      <DashboardBody>
        {isSidebarOpen && <SidebarBackdrop onClick={() => setIsSidebarOpen(false)} />}

        {/* --- Sidebar (Room Selector) --- */}
        <Sidebar open={isSidebarOpen}>
          <SidebarSearchWrap>
            <SearchContainer>
              <Search size={14} />
              <input
                type="text"
                placeholder="Search rooms, device IDs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </SearchContainer>
          </SidebarSearchWrap>

          <SidebarTitle>Monitoring Rooms ({filteredRooms.length})</SidebarTitle>

          <RoomsList>
            {filteredRooms.length === 0 ? (
              <div className="no-devices">No active rooms found. Run detection clients to register.</div>
            ) : (
              filteredRooms.map(room => {
                const payload = room.latestPayload
                const alertLevel = payload?.population_data?.alert_level || 'NORMAL'
                const count = payload?.population_data?.current_count || 0
                const location = payload?.device_info?.location || 'Unknown Location'

                return (
                  <RoomCard
                    key={room.roomId}
                    selected={selectedRoomId === room.roomId}
                    status={alertLevel.toLowerCase() === 'critical' ? 'critical' : alertLevel.toLowerCase() === 'warning' ? 'warning' : 'normal'}
                    onClick={() => handleSelectRoom(room.roomId)}
                  >
                    <div className="card-header-row">
                      <div className="card-title" title={room.roomId}>
                        {room.roomId.replace('device:', '')}
                      </div>
                      <div className="card-time">
                        {new Date(room.lastSeenAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </div>
                    </div>
                    <div className="card-meta">
                      <Video size={11} />
                      <span>{location}</span>
                    </div>

                    <div className="card-stats-row">
                      <div className="card-metric">
                        <Users size={12} />
                        <span>Occupants: <strong>{count}</strong></span>
                      </div>
                      <span className={`card-badge ${alertLevel.toLowerCase()}`}>
                        {alertLevel}
                      </span>
                    </div>

                    {/* Glowing history sparkline */}
                    {renderSparkline(room.roomId)}
                  </RoomCard>
                )
              })
            )}
          </RoomsList>
        </Sidebar>

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

                {/* Visualizer 1: Glowing Radar Scanner Scope */}
                {/* Visualizer 1: Glowing Radar Scanner Scope */}
                <DashboardPanel>
                  <div className="panel-header">
                    <div className="panel-title">
                      <Map size={14} />
                      <span>Live Radar Positioning Scope (Bird's Eye)</span>
                    </div>
                    <div className="panel-actions">
                      <IconOnlyBtn
                        active={isRadarSweep}
                        onClick={() => setIsRadarSweep(!isRadarSweep)}
                        title="Toggle Radar Sweep Animation"
                      >
                        <RefreshCw size={12} />
                      </IconOnlyBtn>
                    </div>
                  </div>

                  <RadarContainerOuter>
                    <div className="radar-grid-bg"></div>
                    <RadarSweepBeam active={isRadarSweep} />

                    <svg className="radar-svg" viewBox="0 0 800 600">
                      {/* Radar sweep lines */}
                      <g className="radar-center-circles">
                        <circle cx="400" cy="300" r="100" />
                        <circle cx="400" cy="300" r="200" />
                        <circle cx="400" cy="300" r="280" />
                        <line x1="400" y1="20" x2="400" y2="580" stroke="rgba(99, 131, 255, 0.05)" strokeWidth="1" />
                        <line x1="20" y1="300" x2="780" y2="300" stroke="rgba(99, 131, 255, 0.05)" strokeWidth="1" />
                      </g>

                      {/* Display tracked points */}
                      {(activeRoom.latestPayload?.population_data?.tracked_persons || []).map(person => {
                        const isSelected = selectedTrackId === person.track_id
                        const isConfirmed = person.confirmed

                        return (
                          <g
                            key={person.track_id}
                            className={`radar-track-dot ${isSelected ? 'selected' : ''}`}
                            onClick={() => setSelectedTrackId(person.track_id)}
                          >
                            {/* Glow */}
                            <circle
                              cx={person.world_x}
                              cy={person.world_y}
                              r={isSelected ? 16 : 10}
                              fill={isSelected ? 'rgba(94, 124, 240, 0.2)' : 'rgba(255, 255, 255, 0.03)'}
                            />
                            {/* Core */}
                            <circle
                              cx={person.world_x}
                              cy={person.world_y}
                              r={isSelected ? 6 : 4}
                              fill={isSelected ? '#5e7cf0' : isConfirmed ? '#10b981' : '#4b5563'}
                            />
                            {/* Track Label text */}
                            <text
                              x={person.world_x + 8}
                              y={person.world_y - 8}
                              fill={isSelected ? '#5e7cf0' : '#9ca3af'}
                              fontSize="9px"
                              className="radar-track-label"
                            >
                              #{person.track_id}
                            </text>
                          </g>
                        )
                      })}
                    </svg>
                  </RadarContainerOuter>
                </DashboardPanel>

                {/* Visualizer 2: Heatmap Capacity Grid */}
                <DashboardPanel>
                  <div className="panel-header">
                    <div className="panel-title">
                      <Grid size={14} />
                      <span>Occupancy Density Grid Heatmap</span>
                    </div>
                  </div>

                  <div className="heatmap-container">
                    <GridWrapper
                      style={{
                        gridTemplateColumns: `repeat(${gridCols}, 1fr)`,
                        width: '100%',
                        maxWidth: `${gridCols * 48}px`,
                        aspectRatio: `${gridCols} / ${gridRows}`
                      }}
                    >
                      {/* Render Cells */}
                      {Array.from({ length: gridRows }).map((_, rIdx) => {
                        return Array.from({ length: gridCols }).map((_, cIdx) => {
                          const cellData = activeRoom.latestPayload?.population_data?.occupancy_grid?.cells?.find(
                            c => c.row === rIdx && c.col === cIdx
                          ) || { occupant_count: 0, density: 0.0, alert_level: 'NORMAL' }

                          const style = {
                            '--intensity': Math.min(cellData.density, 1.0)
                          }

                          return (
                            <GridCellBox
                              key={`${rIdx}-${cIdx}`}
                              level={cellData.alert_level.toLowerCase()}
                              style={style}
                            >
                              <span>{Math.round(cellData.occupant_count)}</span>

                              <div className="tooltip">
                                <strong>Cell [{rIdx}, {cIdx}]</strong><br />
                                Occupants: {cellData.occupant_count}<br />
                                Density: {Math.round(cellData.density * 100)}%<br />
                                Status: {cellData.alert_level}
                              </div>
                            </GridCellBox>
                          )
                        })
                      })}
                    </GridWrapper>

                    {/* Heatmap Legend */}
                    <div className="heatmap-legend">
                      <div className="legend-card">
                        <div className="legend-box" style={{ background: 'var(--color-safe-bg)', border: '1px solid var(--color-safe)' }}></div>
                        <span>Normal (&lt;{Math.round(warningThreshold * 100)}%)</span>
                      </div>
                      <div className="legend-card">
                        <div className="legend-box" style={{ background: 'var(--color-warning-bg)', border: '1px solid var(--color-warning)' }}></div>
                        <span>Warning ({Math.round(warningThreshold * 100)}%+)</span>
                      </div>
                      <div className="legend-card">
                        <div className="legend-box" style={{ background: 'var(--color-danger-bg)', border: '1px solid var(--color-danger)' }}></div>
                        <span>Critical (&gt;{Math.round(criticalThreshold * 100)}%)</span>
                      </div>
                    </div>
                  </div>
                </DashboardPanel>

              </VisualizersGrid>

              {/* Bottom Row - Data Table & Logs */}
              <DetailsRow>

                {/* Table: Tracked Persons list */}
                <DashboardPanel>
                  <div className="panel-header">
                    <div className="panel-title">
                      <Users size={14} />
                      <span>Identified Crowd Tracking Registrations</span>
                    </div>
                  </div>

                  <div className="table-wrapper">
                    <table className="cyber-table">
                      <thead>
                        <tr>
                          <th>Track ID</th>
                          <th>Status</th>
                          <th>Confidence</th>
                          <th>Age (Frames)</th>
                          <th>Radar Coord (X, Y)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(activeRoom.latestPayload?.population_data?.tracked_persons || []).length === 0 ? (
                          <tr>
                            <td colSpan="5" style={{ textCenter: 'center', color: 'var(--text-muted)' }}>
                              No human vectors identified in visual field.
                            </td>
                          </tr>
                        ) : (
                          (activeRoom.latestPayload?.population_data?.tracked_persons || []).map(person => {
                            const isSelected = selectedTrackId === person.track_id
                            return (
                              <tr
                                key={person.track_id}
                                className={isSelected ? 'selected' : ''}
                                onClick={() => setSelectedTrackId(person.track_id)}
                              >
                                <td><strong style={{ color: 'var(--accent)' }}>#{person.track_id}</strong></td>
                                <td className={person.confirmed ? 'txt-confirmed' : 'txt-pending'}>
                                  {person.confirmed ? 'CONFIRMED' : 'PENDING'}
                                </td>
                                <td>{Math.round(person.confidence * 100)}%</td>
                                <td>{person.age}</td>
                                <td>{Math.round(person.world_x)}px, {Math.round(person.world_y)}px</td>
                              </tr>
                            )
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </DashboardPanel>

                {/* Panel: System logs console & threshold adjusters */}
                <DashboardPanel>
                  <div className="panel-header">
                    <div className="panel-title">
                      <Terminal size={14} />
                      <span>Security Command Console Logs</span>
                    </div>
                  </div>

                  <LogConsole>
                    {logs.map(log => (
                      <div key={log.id} className="log-line">
                        <span className="log-time">[{log.time}]</span>
                        <span className={`log-msg ${log.type}`}>
                          {log.msg}
                        </span>
                      </div>
                    ))}
                    <div ref={consoleEndRef}></div>
                  </LogConsole>

                  {/* Simulator Quick Injectors */}
                  {isSimulated && (
                    <div className="sim-controls-grid">
                      <button className="sim-btn active" onClick={triggerMockCongestion}>
                        <AlertTriangle size={12} /> Inject Crowd Surge
                      </button>
                      <button className="sim-btn" onClick={triggerClearCrowd}>
                        <RefreshCw size={12} /> Reset Crowd Density
                      </button>
                    </div>
                  )}

                  {/* Settings Panel */}
                  <div style={{ marginTop: '16px' }}>
                    <div className="setting-slider">
                      <div className="slider-label">
                        <span>Warning Alert Threshold</span>
                        <span>{Math.round(warningThreshold * 100)}%</span>
                      </div>
                      <input
                        type="range"
                        min="0.4"
                        max="0.85"
                        step="0.05"
                        value={warningThreshold}
                        onChange={(e) => setWarningThreshold(parseFloat(e.target.value))}
                        className="slider-input"
                        disabled
                      />
                    </div>

                    <div className="setting-slider">
                      <div className="slider-label">
                        <span>Critical Alert Threshold</span>
                        <span>{Math.round(criticalThreshold * 100)}%</span>
                      </div>
                      <input
                        type="range"
                        min="0.75"
                        max="0.98"
                        step="0.01"
                        value={criticalThreshold}
                        onChange={(e) => setCriticalThreshold(parseFloat(e.target.value))}
                        className="slider-input"
                        disabled
                      />
                    </div>
                  </div>

                </DashboardPanel>

              </DetailsRow>
            </>
          )}
        </ContentArea>

      </DashboardBody>
    </AppContainer>
  )
}

export default App
