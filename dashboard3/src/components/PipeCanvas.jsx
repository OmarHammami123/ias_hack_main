import { motion } from 'framer-motion';

export function PipeCanvas({ nodes, pipes, valves, leakPipe }) {
  return (
    <div className="relative w-full aspect-[3/2] bg-gradient-to-br from-[#0d1527] to-[#0b0f1c] rounded-xl overflow-hidden border border-white/5">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="pipeBody" x1="0%" y1="0%" x2="100%" y2="30%">
            <stop offset="0%" stopColor="#cfd8e3" />
            <stop offset="45%" stopColor="#9fb3c8" />
            <stop offset="100%" stopColor="#7a8aa8" />
          </linearGradient>
          <linearGradient id="pipeLeak" x1="0%" y1="0%" x2="100%" y2="30%">
            <stop offset="0%" stopColor="#ff8fa3" />
            <stop offset="45%" stopColor="#ff5f6d" />
            <stop offset="100%" stopColor="#ff2d55" />
          </linearGradient>
          <linearGradient id="pipeEdge" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#e5e7eb" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#4b5563" stopOpacity="0.9" />
          </linearGradient>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {pipes.map((pipe) => {
          const start = nodes[pipe.start];
          const end = nodes[pipe.end];
          const isLeak = pipe.id === leakPipe;
          const stroke = isLeak ? 'url(#pipeLeak)' : 'url(#pipeBody)';
          const edgeStroke = 'url(#pipeEdge)';
          const width = isLeak ? 22 : 16;
          const edgeWidth = isLeak ? 26 : 20;
          return (
            <g key={pipe.id}>
              <line
                x1={start.x}
                y1={start.y}
                x2={end.x}
                y2={end.y}
                stroke={edgeStroke}
                strokeWidth={edgeWidth}
                strokeLinecap="round"
                opacity={0.7}
              />
              <line
                x1={start.x}
                y1={start.y}
                x2={end.x}
                y2={end.y}
                stroke={stroke}
                strokeWidth={width}
                strokeLinecap="round"
                filter={isLeak ? 'url(#glow)' : undefined}
              />
              <text x={(start.x + end.x) / 2} y={(start.y + end.y) / 2 - 12} textAnchor="middle" fill="#cbd5e1" fontSize="18">
                {pipe.label}
              </text>
            </g>
          );
        })}

        {valves.map((valve) => (
          <Valve key={valve.id} valve={valve} />
        ))}

        {Object.entries(nodes).map(([id, pos]) => (
          <Node key={id} id={id} pos={pos} />
        ))}

        <AnimateLeak leakPipe={leakPipe} pipes={pipes} nodes={nodes} />
      </svg>
    </div>
  );
}

function Node({ id, pos }) {
  return (
    <g>
      <circle cx={pos.x} cy={pos.y} r={30} fill="#0b1221" stroke="#1f2937" strokeWidth={6} />
      <circle cx={pos.x} cy={pos.y} r={22} fill="#111827" stroke="#21d4fd" strokeWidth={2} />
      <text x={pos.x} y={pos.y + 6} textAnchor="middle" fill="#e5e7eb" fontSize="16" fontWeight="600">
        {id}
      </text>
    </g>
  );
}

function Valve({ valve }) {
  return (
    <g>
      <rect
        x={valve.x - 16}
        y={valve.y - 16}
        width={32}
        height={32}
        rx={6}
        fill="#fbbf24"
        stroke="#111827"
        strokeWidth={2}
      />
      <text x={valve.x} y={valve.y + 30} textAnchor="middle" fill="#cbd5e1" fontSize="14">
        Valve
      </text>
    </g>
  );
}

function AnimateLeak({ leakPipe, pipes, nodes }) {
  if (!leakPipe) return null;
  const pipe = pipes.find((p) => p.id === leakPipe);
  if (!pipe) return null;
  const start = nodes[pipe.start];
  const end = nodes[pipe.end];
  const cx = (start.x + end.x) / 2;
  const cy = (start.y + end.y) / 2;

  return (
    <g>
      <motion.circle
        cx={cx}
        cy={cy}
        r={18}
        fill="none"
        stroke="#ff8fa3"
        strokeWidth={4}
        initial={{ opacity: 0.9, scale: 0.7 }}
        animate={{ opacity: 0, scale: 1.6 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'easeOut' }}
        filter="url(#glow)"
      />
      <motion.circle
        cx={cx}
        cy={cy}
        r={8}
        fill="#ff5f6d"
        initial={{ scale: 0.8, opacity: 0.9 }}
        animate={{ scale: 1.05, opacity: 0.6 }}
        transition={{ duration: 0.8, repeat: Infinity, repeatType: 'reverse', ease: 'easeInOut' }}
        filter="url(#glow)"
      />
    </g>
  );
}
