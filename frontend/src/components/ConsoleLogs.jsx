import React from 'react'
import { Terminal } from 'lucide-react'
import { LogConsole } from '../components'

export default function ConsoleLogs({ logs, consoleLogsRef }) {
  return (
    <>
      <div className="panel-header">
        <div className="panel-title">
          <Terminal size={14} />
          <span>Security Command Console Logs</span>
        </div>
      </div>

      <LogConsole ref={consoleLogsRef}>
        {logs.map(log => (
          <div key={log.id} className="log-line">
            <span className="log-time">[{log.time}]</span>
            <span className={`log-msg ${log.type}`}>
              {log.msg}
            </span>
          </div>
        ))}
      </LogConsole>
    </>
  )
}
