import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PipeCanvas } from './components/PipeCanvas';
import { SensorChart } from './components/SensorChart';
import { network } from './data/network';
import { useSensorStream } from './hooks/useSensorStream';
import './styles.css';

export default function App() {
  const [selectedPipe, setSelectedPipe] = useState(null);
  const { latest, history, anomalyPipes, toggleAnomaly } = useSensorStream();

  const pipeReading  = selectedPipe ? latest[selectedPipe] : null;
  const pipeHistory  = selectedPipe ? (history[selectedPipe] ?? []) : [];
  const isAnomaly    = anomalyPipes.has(selectedPipe);
  const anomalyCount = anomalyPipes.size;

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_20%_20%,rgba(33,212,253,0.08),transparent_25%),radial-gradient(circle_at_80%_10%,rgba(183,33,255,0.08),transparent_25%),#0a0f1c]">
      <div className="max-w-[1440px] mx-auto px-6 py-6">

        {/* ── Header ── */}
        <header className="flex items-center justify-between gap-4 mb-5">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-slate-400">Silent Sabotage — Industrial Leak Detection</p>
            <h1 className="text-2xl font-semibold text-white drop-shadow">Pipe Network Monitor</h1>
          </div>
          <div className="flex items-center gap-4">
            {anomalyCount > 0 && (
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                className="flex items-center gap-1.5 bg-rose-500/15 border border-rose-500/30 rounded-xl px-3 py-1.5"
              >
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500" />
                </span>
                <span className="text-sm font-medium text-rose-300">{anomalyCount} anomal{anomalyCount > 1 ? 'ies' : 'y'}</span>
              </motion.div>
            )}
            <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-3 py-1.5">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-sm text-slate-200">Live</span>
            </div>
          </div>
        </header>

        {/* ── Main grid ── */}
        <div className="grid lg:grid-cols-[1fr,420px] gap-5">

          {/* LEFT: Pipe map + pipe list */}
          <div className="space-y-4">
            {/* Pipe Canvas */}
            <div className="bg-[#0e1529]/80 border border-white/10 rounded-2xl shadow-lg backdrop-blur p-4">
              <PipeCanvas
                nodes={network.nodes}
                pipes={network.pipes}
                valves={network.valves}
                anomalyPipes={anomalyPipes}
                selectedPipe={selectedPipe}
                onSelectPipe={(id) => setSelectedPipe((prev) => (prev === id ? null : id))}
              />
            </div>

            {/* Pipe list bar (scrollable) */}
            <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-thin">
              {network.pipes.map((p) => {
                const sel  = p.id === selectedPipe;
                const anom = anomalyPipes.has(p.id);
                return (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPipe((prev) => (prev === p.id ? null : p.id))}
                    className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all
                      ${sel
                        ? 'bg-cyan-500/20 border-cyan-400/50 text-cyan-300'
                        : anom
                          ? 'bg-rose-500/15 border-rose-500/40 text-rose-300 animate-pulse'
                          : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                      }`}
                  >
                    {p.id}
                    {anom && <span className="ml-1 text-[10px]">!</span>}
                  </button>
                );
              })}
            </div>
          </div>

          {/* RIGHT: Sensor detail panel */}
          <div className="space-y-4">
            {/* KPI quick glance */}
            <div className="grid grid-cols-3 gap-2">
              <KpiCard label="Active Pipes" value={network.pipes.length} />
              <KpiCard label="Anomalies" value={anomalyCount} alert={anomalyCount > 0} />
              <KpiCard label="Timestamp" value={new Date().toLocaleTimeString()} small />
            </div>

            {/* Sensor chart (appears on pipe click) */}
            <div className="bg-[#0e1529]/80 border border-white/10 rounded-2xl backdrop-blur p-4 min-h-[340px]">
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

            {/* Anomaly demo controls */}
            <div className="bg-[#0e1529]/60 border border-white/10 rounded-2xl p-3 space-y-2">
              <p className="text-[11px] uppercase tracking-wider text-slate-500">Demo: toggle anomaly</p>
              <div className="flex flex-wrap gap-1.5">
                {network.pipes.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => toggleAnomaly(p.id)}
                    className={`text-[10px] font-mono px-2 py-1 rounded border transition
                      ${anomalyPipes.has(p.id)
                        ? 'bg-rose-500/20 border-rose-500/40 text-rose-300'
                        : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
                      }`}
                  >
                    {p.id}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ label, value, alert, small }) {
  return (
    <div className={`rounded-xl border px-3 py-2.5 ${alert ? 'border-rose-500/40 bg-rose-500/10' : 'border-white/10 bg-white/5'}`}>
      <p className="text-[10px] uppercase tracking-wider text-slate-400">{label}</p>
      <p className={`font-semibold mt-0.5 ${small ? 'text-sm' : 'text-xl'} ${alert ? 'text-rose-300' : 'text-white'}`}>
        {value}
      </p>
    </div>
  );
}
