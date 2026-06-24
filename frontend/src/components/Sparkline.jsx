export default function Sparkline({ data }) {
  if (!data || data.length < 2) return null

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
