import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { PipeCanvas } from './components/PipeCanvas';
import { KpiPanel } from './components/KpiPanel';
import { PressureSparkline } from './components/PressureSparkline';
import { Spectrogram } from './components/Spectrogram';
import { network } from './data/network';
import './styles.css';

export default function App() {
  const [selectedPipe, setSelectedPipe] = useState('');
  const metrics = useMemo(() => simulateMetrics(selectedPipe), [selectedPipe]);
  const spark = useMemo(() => buildSparkData(selectedPipe), [selectedPipe]);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_20%_20%,rgba(33,212,253,0.08),transparent_25%),radial-gradient(circle_at_80%_10%,rgba(183,33,255,0.08),transparent_25%),#0a0f1c]">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <header className="flex items-center justify-between gap-4 mb-6">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-400">Industrial Leak Network</p>
            <h1 className="text-3xl font-semibold font-display text-white drop-shadow">Visual Pipe Map</h1>
          </div>
          <div className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl px-3 py-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-sm text-slate-200">Live simulation</span>
          </div>
        </header>

        <div className="grid lg:grid-cols-[2fr,1fr] gap-6">
          <div className="bg-panel/80 border border-white/10 rounded-2xl shadow-glow backdrop-blur p-4">
            <div className="flex flex-wrap items-center gap-3 mb-4">
              <label className="text-sm text-slate-300">Select leak location</label>
              <select
                value={selectedPipe}
                onChange={(e) => setSelectedPipe(e.target.value)}
                className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent"
              >
                <option value="">No leak</option>
                {network.pipes.map((p) => (
                  <option key={p.id} value={p.id}>{p.label}</option>
                ))}
              </select>
            </div>
            <PipeCanvas
              nodes={network.nodes}
              pipes={network.pipes}
              valves={network.valves}
              leakPipe={selectedPipe}
            />
          </div>

          <div className="space-y-4">
            <KpiPanel metrics={metrics} />
            <div className="bg-panel/80 border border-white/10 rounded-2xl p-4 backdrop-blur">
              <PressureSparkline data={spark} leak={!!selectedPipe} />
            </div>
            <div className="bg-panel/80 border border-white/10 rounded-2xl p-4 backdrop-blur">
              <Spectrogram leak={!!selectedPipe} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function simulateMetrics(leakPipe) {
  const basePressure = 118;
  const baseFlow = 430;
  const leakDrop = leakPipe ? 22 : 0;
  return {
    pressure: +(basePressure - leakDrop + rand(-2, 2)).toFixed(1),
    flow: +(baseFlow - leakDrop * 1.8 + rand(-8, 8)).toFixed(0),
    leakProb: leakPipe ? +(0.72 + Math.random() * 0.2).toFixed(2) : 0.05,
    updated: new Date().toLocaleTimeString(),
  };
}

function buildSparkData(leakPipe) {
  const points = Array.from({ length: 24 }, (_, i) => {
    const t = -60 + i * 5;
    const base = 118 + Math.sin(i / 3) * 1.2;
    const drop = leakPipe ? 18 : 0;
    return { t, v: +(base - drop + rand(-1.5, 1.5)).toFixed(2) };
  });
  return points;
}

function rand(min, max) {
  return Math.random() * (max - min) + min;
}
