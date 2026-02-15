import { motion } from 'framer-motion';

const TRACES = [
  { key: 'pressureIn',  label: 'Pressure In',   color: '#FBBF24', warnColor: '#FF6B6B', unit: 'psi', icon: 'M' },
  { key: 'pressureOut', label: 'Pressure Out',   color: '#2DD4BF', warnColor: '#FF6B6B', unit: 'psi', icon: 'M' },
  { key: 'temperature', label: 'Temperature',    color: '#F59E0B', warnColor: '#FF8A80', unit: 'C',   icon: 'T' },
  { key: 'humidity',    label: 'Humidity',        color: '#34D399', warnColor: '#FF8A80', unit: '%',   icon: 'H' },
];

const W = 480;
const H = 90;
const PAD = 6;

/**
 * SensorChart – 4 real-time trace cards for the selected pipe.
 */
export function SensorChart({ pipeId, history, latest, isAnomaly }) {
  if (!pipeId) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-stone-500 select-none gap-3">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" className="text-stone-600">
          <path d="M4 12h16M4 12a2 2 0 01-2-2V6a2 2 0 012-2h16a2 2 0 012 2v4a2 2 0 01-2 2M4 12a2 2 0 00-2 2v4a2 2 0 002 2h16a2 2 0 002-2v-4a2 2 0 00-2-2" />
        </svg>
        <p className="text-sm font-display">Select a pipe to inspect sensors</p>
      </div>
    );
  }

  return (
    <motion.div
      key={pipeId}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="space-y-3"
    >
      {/* header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-mono text-xs font-bold ${
            isAnomaly
              ? 'bg-coral-500/15 text-coral-400 ring-1 ring-coral-500/30'
              : 'bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/25'
          }`}>
            {pipeId.slice(-3)}
          </div>
          <div>
            <span className="font-display font-semibold text-white text-lg">{pipeId}</span>
            {isAnomaly && (
              <motion.span
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                className="ml-2 inline-flex items-center gap-1 text-[10px] font-mono font-bold uppercase tracking-wider text-coral-400 bg-coral-500/10 px-2 py-0.5 rounded ring-1 ring-coral-500/20"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-coral-500 animate-pulse" />
                LEAK DETECTED
              </motion.span>
            )}
          </div>
        </div>
        <span className="text-[11px] font-mono text-stone-500">
          {latest ? new Date(latest.ts).toLocaleTimeString() : '---'}
        </span>
      </div>

      {/* 4 trace charts in 2x2 grid */}
      <div className="grid grid-cols-2 gap-2.5">
        {TRACES.map((t) => (
          <TraceCard key={t.key} trace={t} history={history} latest={latest} isAnomaly={isAnomaly} />
        ))}
      </div>
    </motion.div>
  );
}

function TraceCard({ trace, history, latest, isAnomaly }) {
  const data = history.map((d) => d[trace.key]);
  const value = latest?.[trace.key] ?? '---';

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
  const lineColor = warn ? trace.warnColor : trace.color;

  // Generate unique gradient ID per trace
  const gradId = `grad-${trace.key}`;

  return (
    <div className={`rounded-xl p-3 transition-all ${
      warn
        ? 'bg-coral-500/[0.06] ring-1 ring-coral-500/15'
        : 'bg-white/[0.02] ring-1 ring-white/[0.04] hover:ring-white/[0.08]'
    }`}>
      {/* top row: label + live value */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: lineColor }} />
          <p className="text-[10px] font-display font-medium uppercase tracking-wider text-stone-500">{trace.label}</p>
        </div>
        <div className="flex items-baseline gap-0.5">
          <p className={`text-sm font-mono font-bold ${warn ? 'text-coral-400' : 'text-white'}`}>
            {typeof value === 'number' ? value.toFixed(1) : value}
          </p>
          <span className="text-[9px] font-mono text-stone-600">{trace.unit}</span>
        </div>
      </div>

      {/* SVG chart */}
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-14" preserveAspectRatio="none">
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={lineColor} stopOpacity="0.25" />
            <stop offset="100%" stopColor={lineColor} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* horizontal grid lines */}
        {[0.25, 0.5, 0.75].map((frac) => (
          <line key={frac} x1={PAD} x2={W - PAD}
            y1={PAD + frac * (H - 2 * PAD)} y2={PAD + frac * (H - 2 * PAD)}
            stroke="#292524" strokeWidth={0.5} strokeDasharray="3,6" />
        ))}

        {data.length > 1 && (
          <>
            {/* gradient area fill */}
            <polygon
              points={`${PAD},${H - PAD} ${points} ${PAD + ((W - 2 * PAD) / Math.max(data.length - 1, 1)) * (data.length - 1)},${H - PAD}`}
              fill={`url(#${gradId})`}
            />
            {/* line */}
            <polyline
              points={points}
              fill="none"
              stroke={lineColor}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ filter: `drop-shadow(0 0 4px ${lineColor}40)` }}
            />
            {/* latest point with glow */}
            {(() => {
              const lastX = PAD + ((W - 2 * PAD) / Math.max(data.length - 1, 1)) * (data.length - 1);
              const lastY = H - PAD - ((data[data.length - 1] - min) / range) * (H - 2 * PAD);
              return (
                <>
                  <circle cx={lastX} cy={lastY} r={6} fill={lineColor} opacity={0.15} />
                  <circle cx={lastX} cy={lastY} r={3} fill={lineColor} />
                  <circle cx={lastX} cy={lastY} r={1.5} fill="#050608" />
                </>
              );
            })()}
          </>
        )}
      </svg>
    </div>
  );
}
