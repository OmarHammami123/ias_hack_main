import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PipeCanvas } from './components/PipeCanvas';
import { SensorChart } from './components/SensorChart';
import { network } from './data/network';
import { useSensorStream } from './hooks/useSensorStream';
import './styles.css';

/* ── Micro-icon SVGs ── */
const IconPipe = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M4 12h16M4 12a2 2 0 01-2-2V6a2 2 0 012-2h16a2 2 0 012 2v4a2 2 0 01-2 2M4 12a2 2 0 00-2 2v4a2 2 0 002 2h16a2 2 0 002-2v-4a2 2 0 00-2-2" />
  </svg>
);
const IconAlert = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
    <path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
  </svg>
);
const IconClock = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
  </svg>
);
const IconBrain = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M12 2a7 7 0 017 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 01-2 2h-4a2 2 0 01-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 017-7z" />
    <path d="M9 21h6M10 17v4M14 17v4" />
  </svg>
);

export default function App() {
  const [selectedPipe, setSelectedPipe] = useState(null);
  const { latest, history, anomalyPipes, scores, connected } = useSensorStream();

  const pipeReading  = selectedPipe ? latest[selectedPipe] : null;
  const pipeHistory  = selectedPipe ? (history[selectedPipe] ?? []) : [];
  const isAnomaly    = anomalyPipes.has(selectedPipe);
  const anomalyCount = anomalyPipes.size;

  return (
    <div className="min-h-screen bg-bg bg-dots">
      {/* Ambient glow blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-32 -left-32 w-96 h-96 bg-amber-500/[0.04] rounded-full blur-[120px]" />
        <div className="absolute -bottom-48 -right-48 w-[600px] h-[600px] bg-teal-400/[0.03] rounded-full blur-[140px]" />
      </div>

      <div className="relative max-w-[1480px] mx-auto px-5 py-5">

        {/* ═══════ HEADER ═══════ */}
        <header className="flex items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-4">
            {/* Logo mark */}
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center shadow-glow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#050608" strokeWidth="2.5" strokeLinecap="round">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-display font-semibold text-white tracking-tight">
                Silent Sabotage
              </h1>
              <p className="text-[11px] font-mono uppercase tracking-[0.2em] text-stone-500">
                Industrial Air Leak Detection System
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Anomaly badge */}
            {anomalyCount > 0 && (
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="flex items-center gap-2 glass-card rounded-xl px-3.5 py-2"
                style={{ borderColor: 'rgba(255,107,107,0.25)' }}
              >
                <span className="relative flex h-2.5 w-2.5">
                  <span className="pulse-ring absolute inline-flex h-full w-full rounded-full bg-coral-500" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-coral-500" />
                </span>
                <span className="text-sm font-display font-medium text-coral-400">
                  {anomalyCount} Leak{anomalyCount > 1 ? 's' : ''} Detected
                </span>
              </motion.div>
            )}

            {/* Connection status */}
            <div className={`flex items-center gap-2 glass-card rounded-xl px-3.5 py-2 ${
              connected ? 'border-emerald-500/20' : 'border-amber-500/20'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                connected ? 'bg-emerald-400 animate-pulse-slow' : 'bg-amber-400 animate-bounce'
              }`} />
              <span className="text-xs font-mono text-stone-400">
                {connected ? 'LIVE' : 'CONNECTING'}
              </span>
            </div>
          </div>
        </header>

        {/* ═══════ KPI ROW ═══════ */}
        <div className="grid grid-cols-4 gap-3 mb-5">
          <KpiCard
            icon={<IconPipe />}
            label="Active Pipes"
            value={network.pipes.length}
            accent="amber"
          />
          <KpiCard
            icon={<IconAlert />}
            label="Active Leaks"
            value={anomalyCount}
            accent={anomalyCount > 0 ? 'coral' : 'teal'}
            alert={anomalyCount > 0}
          />
          <KpiCard
            icon={<IconBrain />}
            label="Model"
            value="Isolation Forest"
            small
            accent="teal"
          />
          <KpiCard
            icon={<IconClock />}
            label="Updated"
            value={new Date().toLocaleTimeString()}
            small
            accent="amber"
          />
        </div>

        {/* ═══════ MAIN GRID ═══════ */}
        <div className="grid lg:grid-cols-[1fr,440px] gap-5">

          {/* ── LEFT COLUMN ── */}
          <div className="space-y-4">
            {/* Pipe network canvas */}
            <div className="glass-card rounded-2xl p-4 gradient-border">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-display font-semibold text-white tracking-tight">
                  Network Topology
                </h2>
                <span className="text-[10px] font-mono text-stone-500 bg-surface3 px-2 py-0.5 rounded">
                  {network.pipes.length} segments / {Object.keys(network.nodes).length} nodes
                </span>
              </div>
              <PipeCanvas
                nodes={network.nodes}
                pipes={network.pipes}
                valves={network.valves}
                anomalyPipes={anomalyPipes}
                selectedPipe={selectedPipe}
                onSelectPipe={(id) => setSelectedPipe((prev) => (prev === id ? null : id))}
              />
            </div>

            {/* Pipe selector strip */}
            <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-thin">
              {network.pipes.map((p) => {
                const sel  = p.id === selectedPipe;
                const anom = anomalyPipes.has(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPipe((prev) => (prev === p.id ? null : p.id))}
                    className={`flex-shrink-0 group relative px-3.5 py-2 rounded-lg text-xs font-mono font-medium transition-all
                      ${sel
                        ? 'bg-amber-500/15 text-amber-400 ring-1 ring-amber-500/40'
                        : anom
                          ? 'bg-coral-500/10 text-coral-400 ring-1 ring-coral-500/30'
                          : 'bg-surface2 text-stone-400 hover:bg-surface3 hover:text-stone-300 ring-1 ring-white/[0.04]'
                      }`}
                  >
                    <span className="flex items-center gap-1.5">
                      {p.id}
                      {anom && (
                        <span className="relative flex h-1.5 w-1.5">
                          <span className="pulse-ring absolute inline-flex h-full w-full rounded-full bg-coral-500" />
                          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-coral-500" />
                        </span>
                      )}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* ── RIGHT COLUMN ── */}
          <div className="space-y-4">
            {/* Sensor charts panel */}
            <div className="glass-card rounded-2xl p-4 min-h-[380px]">
              <AnimatePresence mode="wait">
                <SensorChart
                  key={selectedPipe ?? '__empty'}
                  pipeId={selectedPipe}
                  history={pipeHistory}
                  latest={pipeReading}
                  isAnomaly={isAnomaly}
                />
              </AnimatePresence>
            </div>

            {/* Model scores panel */}
            <div className="glass-card rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-5 h-5 rounded bg-teal-400/10 flex items-center justify-center">
                  <IconBrain />
                </div>
                <p className="text-[11px] font-display font-semibold uppercase tracking-wider text-stone-400">
                  Anomaly Scores
                </p>
              </div>
              <div className="space-y-1.5">
                {network.pipes.map((p) => {
                  const s = scores[p.id];
                  const isAnom = anomalyPipes.has(p.id);
                  const sel = p.id === selectedPipe;
                  // Normalize score for bar width (anomaly scores are typically -0.5 to 0.5)
                  const barWidth = s != null ? Math.min(Math.max((s + 0.5) * 100, 2), 100) : 0;

                  return (
                    <div
                      key={p.id}
                      onClick={() => setSelectedPipe((prev) => (prev === p.id ? null : p.id))}
                      className={`group flex items-center gap-3 text-xs font-mono px-3 py-2 rounded-lg cursor-pointer transition-all
                        ${isAnom
                          ? 'bg-coral-500/10 ring-1 ring-coral-500/25'
                          : sel
                            ? 'bg-amber-500/10 ring-1 ring-amber-500/20'
                            : 'bg-surface2/60 hover:bg-surface3 ring-1 ring-white/[0.03]'
                        }`}
                    >
                      <span className={`w-12 font-semibold ${isAnom ? 'text-coral-400' : sel ? 'text-amber-400' : 'text-stone-400'}`}>
                        {p.id}
                      </span>
                      {/* Score bar */}
                      <div className="flex-1 h-1.5 bg-surface3 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full score-bar transition-all ${
                            isAnom ? 'bg-gradient-to-r from-coral-500 to-coral-400' : 'bg-gradient-to-r from-teal-500/40 to-teal-400/60'
                          }`}
                          style={{ width: `${barWidth}%` }}
                        />
                      </div>
                      <span className={`w-14 text-right tabular-nums ${isAnom ? 'text-coral-400 font-bold' : 'text-stone-500'}`}>
                        {s != null ? s.toFixed(4) : '---'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* ═══════ FOOTER ═══════ */}
        <footer className="mt-6 flex items-center justify-between text-[10px] font-mono text-stone-600 border-t border-white/[0.04] pt-3">
          <span>Silent Sabotage v2.0 --- Isolation Forest + Pressure Differential</span>
          <span>Hackathon 2025</span>
        </footer>
      </div>
    </div>
  );
}

/* ── KPI Card ── */
function KpiCard({ icon, label, value, accent = 'amber', alert, small }) {
  const colors = {
    amber: { ring: 'ring-amber-500/15', icon: 'text-amber-400', bg: 'bg-amber-500/10', val: 'text-amber-50' },
    teal:  { ring: 'ring-teal-500/15',  icon: 'text-teal-400',  bg: 'bg-teal-500/10',  val: 'text-teal-50' },
    coral: { ring: 'ring-coral-500/20', icon: 'text-coral-400', bg: 'bg-coral-500/10', val: 'text-coral-400' },
  }[accent];

  return (
    <div className={`glass-card glass-card-hover rounded-xl px-4 py-3 ring-1 ${colors.ring}`}>
      <div className="flex items-center gap-2 mb-1.5">
        <div className={`w-6 h-6 rounded-md ${colors.bg} flex items-center justify-center ${colors.icon}`}>
          {icon}
        </div>
        <p className="text-[10px] font-display uppercase tracking-wider text-stone-500">{label}</p>
      </div>
      <p className={`font-display font-semibold ${small ? 'text-sm' : 'text-2xl'} ${alert ? colors.val : 'text-white'}`}>
        {value}
      </p>
    </div>
  );
}
