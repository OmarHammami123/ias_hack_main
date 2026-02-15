import { motion } from 'framer-motion';

/**
 * PipeCanvas — interactive SVG pipe network with industrial amber theme.
 *
 * Props:
 *   nodes, pipes, valves           – topology from network.js
 *   anomalyPipes: Set<string>      – pipe IDs currently flagged anomalous
 *   selectedPipe: string | null    – the pipe the user clicked on
 *   onSelectPipe: (id) => void     – click callback
 */
export function PipeCanvas({ nodes, pipes, valves, anomalyPipes, selectedPipe, onSelectPipe }) {
  return (
    <div className="relative w-full aspect-[3/2] bg-gradient-to-br from-[#070809] to-[#0a0c12] rounded-xl overflow-hidden ring-1 ring-white/[0.04]">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid meet">
        <defs>
          {/* ── Pipe gradients ── */}
          <linearGradient id="pipeNormal" x1="0%" y1="0%" x2="100%" y2="30%">
            <stop offset="0%" stopColor="#78716c" />
            <stop offset="50%" stopColor="#57534e" />
            <stop offset="100%" stopColor="#44403c" />
          </linearGradient>
          <linearGradient id="pipeLeak" x1="0%" y1="0%" x2="100%" y2="30%">
            <stop offset="0%" stopColor="#FF8A80" />
            <stop offset="50%" stopColor="#FF6B6B" />
            <stop offset="100%" stopColor="#EF4444" />
          </linearGradient>
          <linearGradient id="pipeSelected" x1="0%" y1="0%" x2="100%" y2="30%">
            <stop offset="0%" stopColor="#FBBF24" />
            <stop offset="50%" stopColor="#F59E0B" />
            <stop offset="100%" stopColor="#D97706" />
          </linearGradient>
          <linearGradient id="pipeEdge" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#a8a29e" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#292524" stopOpacity="0.6" />
          </linearGradient>

          {/* ── Node gradient ── */}
          <radialGradient id="nodeGrad" cx="40%" cy="35%">
            <stop offset="0%" stopColor="#1a1d28" />
            <stop offset="100%" stopColor="#0c0e14" />
          </radialGradient>

          {/* ── Glow filters ── */}
          <filter id="leakGlow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <filter id="selectGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <filter id="amberGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feFlood floodColor="#FBBF24" floodOpacity="0.4" result="color" />
            <feComposite in="color" in2="blur" operator="in" result="glow" />
            <feMerge><feMergeNode in="glow" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>

          {/* ── Flow dash pattern ── */}
          <pattern id="flowDash" patternUnits="userSpaceOnUse" width="24" height="6" patternTransform="rotate(0)">
            <rect x="0" y="0" width="14" height="6" rx="3" fill="rgba(251,191,36,0.15)" />
          </pattern>
        </defs>

        {/* ── Subtle grid ── */}
        <pattern id="bgGrid" width="40" height="40" patternUnits="userSpaceOnUse">
          <circle cx="20" cy="20" r="0.5" fill="rgba(251,191,36,0.06)" />
        </pattern>
        <rect width="1200" height="800" fill="url(#bgGrid)" />

        {/* ── Pipes ── */}
        {pipes.map((pipe) => {
          const s = nodes[pipe.start];
          const e = nodes[pipe.end];
          const isAnomaly  = anomalyPipes?.has(pipe.id);
          const isSelected = pipe.id === selectedPipe;
          const stroke     = isAnomaly ? 'url(#pipeLeak)' : isSelected ? 'url(#pipeSelected)' : 'url(#pipeNormal)';
          const width      = isAnomaly ? 20 : isSelected ? 18 : 14;
          const edgeWidth  = width + 4;
          const mx = (s.x + e.x) / 2;
          const my = (s.y + e.y) / 2;

          return (
            <g
              key={pipe.id}
              className="cursor-pointer"
              onClick={() => onSelectPipe?.(pipe.id)}
            >
              {/* hover hit area */}
              <line x1={s.x} y1={s.y} x2={e.x} y2={e.y}
                stroke="transparent" strokeWidth={40} />
              {/* metallic edge */}
              <line x1={s.x} y1={s.y} x2={e.x} y2={e.y}
                stroke="url(#pipeEdge)" strokeWidth={edgeWidth} strokeLinecap="round" opacity={0.5} />
              {/* main body */}
              <line x1={s.x} y1={s.y} x2={e.x} y2={e.y}
                stroke={stroke} strokeWidth={width} strokeLinecap="round"
                filter={isAnomaly ? 'url(#leakGlow)' : isSelected ? 'url(#selectGlow)' : undefined} />
              {/* animated flow dashes (only on normal/selected pipes) */}
              {!isAnomaly && (
                <line x1={s.x} y1={s.y} x2={e.x} y2={e.y}
                  stroke="rgba(251,191,36,0.08)" strokeWidth={width - 4} strokeLinecap="round"
                  strokeDasharray="8 16" className="animate-flow" />
              )}

              {/* ID badge */}
              <rect x={mx - 30} y={my - 26} width={60} height={20} rx={6}
                fill="rgba(5,6,8,0.75)" stroke={isAnomaly ? '#FF6B6B' : isSelected ? '#FBBF24' : '#44403c'}
                strokeWidth={1.2} />
              <text x={mx} y={my - 13} textAnchor="middle"
                fill={isAnomaly ? '#FF8A80' : isSelected ? '#FBBF24' : '#a8a29e'}
                fontSize="11" fontWeight="700" letterSpacing="0.05em">
                {pipe.id}
              </text>
              {/* sub label */}
              <text x={mx} y={my + 4} textAnchor="middle" fill="#57534e" fontSize="10">
                {pipe.label}
              </text>
            </g>
          );
        })}

        {/* ── Valves (diamond shape) ── */}
        {valves.map((valve) => (
          <Valve key={valve.id} valve={valve} />
        ))}

        {/* ── Nodes (hexagonal) ── */}
        {Object.entries(nodes).map(([id, pos]) => (
          <HexNode key={id} id={pos.label || id} pos={pos} />
        ))}

        {/* ── Leak animations ── */}
        {pipes.filter((p) => anomalyPipes?.has(p.id)).map((pipe) => (
          <AnimateLeak key={`leak-${pipe.id}`} pipe={pipe} nodes={nodes} />
        ))}
      </svg>
    </div>
  );
}

/* ── Hexagonal node ── */
function HexNode({ id, pos }) {
  const r = 26;
  const hex = Array.from({ length: 6 }, (_, i) => {
    const angle = (Math.PI / 3) * i - Math.PI / 6;
    return `${pos.x + r * Math.cos(angle)},${pos.y + r * Math.sin(angle)}`;
  }).join(' ');

  return (
    <g>
      {/* outer ring */}
      <polygon points={hex} fill="none" stroke="#44403c" strokeWidth={3} />
      {/* inner fill */}
      <polygon points={hex} fill="url(#nodeGrad)" stroke="#FBBF24" strokeWidth={1.2} opacity={0.9} />
      {/* label */}
      <text x={pos.x} y={pos.y + 4} textAnchor="middle" fill="#d6d3d1" fontSize="11" fontWeight="600" letterSpacing="0.02em">
        {id}
      </text>
    </g>
  );
}

/* ── Valve (rotated diamond) ── */
function Valve({ valve }) {
  return (
    <g>
      <rect x={valve.x - 12} y={valve.y - 12} width={24} height={24} rx={4}
        fill="#D97706" stroke="#050608" strokeWidth={2}
        transform={`rotate(45 ${valve.x} ${valve.y})`} />
      <text x={valve.x} y={valve.y + 30} textAnchor="middle" fill="#78716c" fontSize="10" fontWeight="500">
        VALVE
      </text>
    </g>
  );
}

/* ── Animated leak pulse ── */
function AnimateLeak({ pipe, nodes }) {
  const s = nodes[pipe.start];
  const e = nodes[pipe.end];
  const cx = (s.x + e.x) / 2;
  const cy = (s.y + e.y) / 2;

  return (
    <g>
      {/* outer expanding ring */}
      <motion.circle cx={cx} cy={cy} r={20} fill="none" stroke="#FF6B6B" strokeWidth={3}
        initial={{ opacity: 0.8, scale: 0.6 }}
        animate={{ opacity: 0, scale: 2.0 }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeOut' }}
        filter="url(#leakGlow)" />
      {/* second ring (staggered) */}
      <motion.circle cx={cx} cy={cy} r={16} fill="none" stroke="#FF8A80" strokeWidth={2}
        initial={{ opacity: 0.6, scale: 0.7 }}
        animate={{ opacity: 0, scale: 1.8 }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeOut', delay: 0.5 }}
      />
      {/* center dot */}
      <motion.circle cx={cx} cy={cy} r={6} fill="#FF6B6B"
        initial={{ scale: 0.85, opacity: 0.8 }}
        animate={{ scale: 1.1, opacity: 0.5 }}
        transition={{ duration: 0.7, repeat: Infinity, repeatType: 'reverse', ease: 'easeInOut' }}
        filter="url(#leakGlow)" />
      {/* warning icon */}
      <text x={cx} y={cy + 4} textAnchor="middle" fill="#050608" fontSize="8" fontWeight="900">
        !
      </text>
    </g>
  );
}
