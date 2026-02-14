import { useMemo } from 'react';

export function Spectrogram({ leak }) {
  const grid = useMemo(() => buildSpectrogram(leak), [leak]);
  const max = Math.max(...grid.flat());
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-slate-300">Acoustic spectrogram (simulated)</p>
        <span className="text-xs text-slate-400">mic feed mock</span>
      </div>
      <div className="grid grid-cols-24 gap-[2px] bg-white/5 p-[2px] rounded-lg border border-white/5" style={{ gridTemplateColumns: 'repeat(24, minmax(0, 1fr))' }}>
        {grid.map((row, ri) => (
          <div key={ri} className="flex gap-[2px]" style={{ gridColumn: `span 24` }}>
            {row.map((cell, ci) => (
              <div
                key={ci}
                className="h-4 w-full rounded-sm"
                style={{
                  background: leak
                    ? `linear-gradient(180deg, rgba(255,95,109,${cell / max}), rgba(33,212,253,${cell / max}))`
                    : `linear-gradient(180deg, rgba(33,212,253,${cell / max}), rgba(183,33,255,${cell / max}))`,
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

function buildSpectrogram(leak) {
  const rows = 16;
  const cols = 24;
  const base = Array.from({ length: rows }, () => Array.from({ length: cols }, () => 0));
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const band = Math.sin((r / rows) * Math.PI) * 0.4;
      const noise = Math.random() * 0.25;
      const leakBurst = leak ? Math.max(0, 1.4 - Math.abs(c - cols * 0.65) / cols * 2.4) : 0.15;
      base[r][c] = band + noise + leakBurst;
    }
  }
  return base;
}
