import { motion } from 'framer-motion';

export function PressureSparkline({ data, leak }) {
  const min = Math.min(...data.map((d) => d.v)) - 2;
  const max = Math.max(...data.map((d) => d.v)) + 2;
  const points = data
    .map((d, i) => {
      const x = (i / (data.length - 1)) * 100;
      const y = 100 - ((d.v - min) / (max - min)) * 100;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-slate-300">Pressure (last 2h)</p>
        {leak ? (
          <span className="text-xs text-rose-300">leak drop detected</span>
        ) : (
          <span className="text-xs text-emerald-300">stable</span>
        )}
      </div>
      <svg viewBox="0 0 100 100" className="w-full h-24 bg-white/5 rounded-lg border border-white/5">
        <polyline
          points={points}
          fill="none"
          stroke={leak ? '#ff5f6d' : '#21d4fd'}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <motion.circle
          r="2.6"
          fill={leak ? '#ff5f6d' : '#21d4fd'}
          initial={{ cx: 0, cy: 100 - ((data[0].v - min) / (max - min)) * 100 }}
          animate={{
            cx: 100,
            cy: 100 - ((data[data.length - 1].v - min) / (max - min)) * 100,
          }}
          transition={{ duration: 2.2, repeat: Infinity, repeatType: 'reverse', ease: 'easeInOut' }}
        />
      </svg>
    </div>
  );
}
