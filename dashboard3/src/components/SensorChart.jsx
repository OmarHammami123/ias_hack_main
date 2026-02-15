import { motion } from 'framer-motion';

const TRACES = [
  { key: 'pressureIn',  label: 'Pressure In (psi)',  color: '#21d4fd', unit: 'psi' },
  { key: 'pressureOut', label: 'Pressure Out (psi)', color: '#b721ff', unit: 'psi' },
  { key: 'temperature', label: 'Temperature (°C)',   color: '#fbbf24', unit: '°C' },
  { key: 'humidity',    label: 'Humidity (%)',        color: '#34d399', unit: '%' },
];

const W = 480;    // svg viewBox width
const H = 100;    // svg viewBox height per chart
const PAD = 4;

/**
 * SensorChart – shows 4 real-time line charts for the selected pipe.
 *
 * Props:
 *   pipeId   – selected pipe ID
 *   history  – array of { pressureIn, pressureOut, temperature, humidity, ts }
 *   latest   – most recent reading (same shape)
 *   isAnomaly – boolean
 */
export function SensorChart({ pipeId, history, latest, isAnomaly }) {
  if (!pipeId) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500 text-sm select-none">
        Click a pipe on the map to inspect its sensors
      </div>
    );
  }

  return (
    <motion.div
      key={pipeId}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-3"
    >
      {/* header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-white font-semibold text-lg">{pipeId}</span>
          {isAnomaly && (
            <span className="ml-2 text-xs font-bold uppercase tracking-wider text-rose-400 bg-rose-400/15 px-2 py-0.5 rounded">
              ANOMALY
            </span>
          )}
        </div>
        <span className="text-xs text-slate-400">
          {latest ? new Date(latest.ts).toLocaleTimeString() : '—'}
        </span>
      </div>

      {/* 4 trace charts */}
      <div className="grid grid-cols-2 gap-3">
        {TRACES.map((t) => (
          <TraceCard key={t.key} trace={t} history={history} latest={latest} isAnomaly={isAnomaly} />
        ))}
      </div>
    </motion.div>
  );
}

function TraceCard({ trace, history, latest, isAnomaly }) {
  const data = history.map((d) => d[trace.key]);
  const value = latest?.[trace.key] ?? '—';

  // adaptive min/max
  const min = data.length ? Math.min(...data) - 1 : 0;
  const max = data.length ? Math.max(...data) + 1 : 1;
  const range = max - min || 1;

  const points = data
    .map((v, i) => {
      const x = PAD + ((W - 2 * PAD) / Math.max(data.length - 1, 1)) * i;
      const y = H - PAD - ((v - min) / range) * (H - 2 * PAD);
      return `${x},${y}`;
    })
    .join(' ');

  const warn = isAnomaly && (trace.key === 'pressureOut' || trace.key === 'humidity');

  return (
    <div className="rounded-xl bg-white/[0.04] border border-white/[0.06] p-3">
      {/* top row: label + live value */}
      <div className="flex items-center justify-between mb-1.5">
        <p className="text-[11px] uppercase tracking-wider text-slate-400">{trace.label}</p>
        <p className={`text-sm font-mono font-semibold ${warn ? 'text-rose-400' : 'text-white'}`}>
          {typeof value === 'number' ? value.toFixed(1) : value}
          <span className="text-[10px] text-slate-500 ml-0.5">{trace.unit}</span>
        </p>
      </div>

      {/* SVG line chart */}
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-16" preserveAspectRatio="none">
        {/* horizontal grid lines */}
        {[0.25, 0.5, 0.75].map((frac) => (
          <line key={frac} x1={PAD} x2={W - PAD}
            y1={PAD + frac * (H - 2 * PAD)} y2={PAD + frac * (H - 2 * PAD)}
            stroke="#334155" strokeWidth={0.5} strokeDasharray="4,4" />
        ))}

        {data.length > 1 && (
          <>
            {/* area fill under the line */}
            <polygon
              points={`${PAD},${H - PAD} ${points} ${PAD + ((W - 2 * PAD) / Math.max(data.length - 1, 1)) * (data.length - 1)},${H - PAD}`}
              fill={warn ? 'rgba(255,95,109,0.08)' : `${trace.color}10`}
            />
            {/* line */}
            <polyline
              points={points}
              fill="none"
              stroke={warn ? '#ff5f6d' : trace.color}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* latest point dot */}
            {(() => {
              const lastX = PAD + ((W - 2 * PAD) / Math.max(data.length - 1, 1)) * (data.length - 1);
              const lastY = H - PAD - ((data[data.length - 1] - min) / range) * (H - 2 * PAD);
              return <circle cx={lastX} cy={lastY} r={3.5} fill={warn ? '#ff5f6d' : trace.color} />;
            })()}
          </>
        )}
      </svg>
    </div>
  );
}
