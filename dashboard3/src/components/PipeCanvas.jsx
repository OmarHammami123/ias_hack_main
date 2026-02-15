import { motion } from 'framer-motion';

/**
 * PipeCanvas — interactive SVG pipe network.
 *
 * Props:
 *   nodes, pipes, valves           – topology from network.js
 *   anomalyPipes: Set<string>      – pipe IDs currently flagged anomalous
 *   selectedPipe: string | null    – the pipe the user clicked on
 *   onSelectPipe: (id) => void     – click callback
 */
export function PipeCanvas({ nodes, pipes, valves, anomalyPipes, selectedPipe, onSelectPipe }) {
  return (
    <div className="relative w-full aspect-[3/2] bg-gradient-to-br from-[#0d1527] to-[#0b0f1c] rounded-xl overflow-hidden border border-white/5">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid meet">
        <defs>
          {/* normal pipe gradient */}
          <linearGradient id="pipeBody" x1="0%" y1="0%" x2="100%" y2="30%">
            <stop offset="0%" stopColor="#cfd8e3" />
            <stop offset="45%" stopColor="#9fb3c8" />
            <stop offset="100%" stopColor="#7a8aa8" />
          </linearGradient>
          {/* anomaly / leak gradient */}
          <linearGradient id="pipeLeak" x1="0%" y1="0%" x2="100%" y2="30%">
            <stop offset="0%" stopColor="#ff8fa3" />
            <stop offset="45%" stopColor="#ff5f6d" />
            <stop offset="100%" stopColor="#ff2d55" />
          </linearGradient>
          {/* selected highlight */}
          <linearGradient id="pipeSelected" x1="0%" y1="0%" x2="100%" y2="30%">
            <stop offset="0%" stopColor="#21d4fd" />
            <stop offset="45%" stopColor="#21d4fd" />
            <stop offset="100%" stopColor="#b721ff" />
          </linearGradient>
          {/* edge shading */}
          <linearGradient id="pipeEdge" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#e5e7eb" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#4b5563" stopOpacity="0.9" />
          </linearGradient>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
          <filter id="selectGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* ── Pipes ── */}
        {pipes.map((pipe) => {
          const s = nodes[pipe.start];
          const e = nodes[pipe.end];
          const isAnomaly  = anomalyPipes?.has(pipe.id);
          const isSelected = pipe.id === selectedPipe;
          const stroke     = isAnomaly ? 'url(#pipeLeak)' : isSelected ? 'url(#pipeSelected)' : 'url(#pipeBody)';
          const width      = isAnomaly ? 22 : isSelected ? 20 : 16;
          const edgeWidth  = width + 4;
          const mx = (s.x + e.x) / 2;
          const my = (s.y + e.y) / 2;

          return (
            <g
              key={pipe.id}
              className="cursor-pointer"
              onClick={() => onSelectPipe?.(pipe.id)}
            >
              {/* hover hit area (invisible wide line) */}
              <line x1={s.x} y1={s.y} x2={e.x} y2={e.y}
                stroke="transparent" strokeWidth={36} />
              {/* edge */}
              <line x1={s.x} y1={s.y} x2={e.x} y2={e.y}
                stroke="url(#pipeEdge)" strokeWidth={edgeWidth} strokeLinecap="round" opacity={0.7} />
              {/* body */}
              <line x1={s.x} y1={s.y} x2={e.x} y2={e.y}
                stroke={stroke} strokeWidth={width} strokeLinecap="round"
                filter={isAnomaly ? 'url(#glow)' : isSelected ? 'url(#selectGlow)' : undefined} />
              {/* ID badge */}
              <rect x={mx - 28} y={my - 24} width={56} height={18} rx={4}
                fill="rgba(0,0,0,0.55)" stroke={isAnomaly ? '#ff5f6d' : isSelected ? '#21d4fd' : '#475569'}
                strokeWidth={1} />
              <text x={mx} y={my - 12} textAnchor="middle" fill={isAnomaly ? '#ff8fa3' : '#e5e7eb'}
                fontSize="12" fontWeight="700">
                {pipe.id}
              </text>
              {/* label */}
              <text x={mx} y={my + 4} textAnchor="middle" fill="#94a3b8" fontSize="11">
                {pipe.label}
              </text>
            </g>
          );
        })}

        {/* ── Valves ── */}
        {valves.map((valve) => (
          <Valve key={valve.id} valve={valve} />
        ))}

        {/* ── Nodes ── */}
        {Object.entries(nodes).map(([id, pos]) => (
          <Node key={id} id={pos.label || id} pos={pos} />
        ))}

        {/* ── Animated leak rings on ALL anomaly pipes ── */}
        {pipes.filter((p) => anomalyPipes?.has(p.id)).map((pipe) => (
          <AnimateLeak key={`leak-${pipe.id}`} pipe={pipe} nodes={nodes} />
        ))}
      </svg>
    </div>
  );
}

function Node({ id, pos }) {
  return (
    <g>
      <circle cx={pos.x} cy={pos.y} r={28} fill="#0b1221" stroke="#1f2937" strokeWidth={5} />
      <circle cx={pos.x} cy={pos.y} r={20} fill="#111827" stroke="#21d4fd" strokeWidth={2} />
      <text x={pos.x} y={pos.y + 5} textAnchor="middle" fill="#e5e7eb" fontSize="13" fontWeight="600">
        {id}
      </text>
    </g>
  );
}

function Valve({ valve }) {
  return (
    <g>
      <rect x={valve.x - 14} y={valve.y - 14} width={28} height={28} rx={5}
        fill="#fbbf24" stroke="#111827" strokeWidth={2} />
      <text x={valve.x} y={valve.y + 28} textAnchor="middle" fill="#cbd5e1" fontSize="12">
        Valve
      </text>
    </g>
  );
}

function AnimateLeak({ pipe, nodes }) {
  const s = nodes[pipe.start];
  const e = nodes[pipe.end];
  const cx = (s.x + e.x) / 2;
  const cy = (s.y + e.y) / 2;

  return (
    <g>
      <motion.circle cx={cx} cy={cy} r={18} fill="none" stroke="#ff8fa3" strokeWidth={4}
        initial={{ opacity: 0.9, scale: 0.7 }}
        animate={{ opacity: 0, scale: 1.6 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'easeOut' }}
        filter="url(#glow)" />
      <motion.circle cx={cx} cy={cy} r={8} fill="#ff5f6d"
        initial={{ scale: 0.8, opacity: 0.9 }}
        animate={{ scale: 1.05, opacity: 0.6 }}
        transition={{ duration: 0.8, repeat: Infinity, repeatType: 'reverse', ease: 'easeInOut' }}
        filter="url(#glow)" />
    </g>
  );
}
