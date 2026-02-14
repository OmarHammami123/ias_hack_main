import { motion } from 'framer-motion';

const cards = [
  { key: 'pressure', label: 'Pressure', unit: 'psi' },
  { key: 'flow', label: 'Flow', unit: 'cfm' },
  { key: 'leakProb', label: 'Leak probability', unit: '' },
  { key: 'updated', label: 'Updated', unit: '' },
];

export function KpiPanel({ metrics }) {
  return (
    <div className="grid grid-cols-2 gap-3 bg-panel/80 border border-white/10 rounded-2xl p-4 backdrop-blur">
      {cards.map((c, idx) => (
        <motion.div
          key={c.key}
          className="rounded-xl border border-white/5 bg-white/5 px-3 py-3 shadow-inner"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.05 }}
        >
          <p className="text-xs uppercase tracking-[0.12em] text-slate-400">{c.label}</p>
          <p className="text-xl font-semibold text-white mt-1">
            {metrics[c.key]} {c.unit}
          </p>
        </motion.div>
      ))}
    </div>
  );
}
