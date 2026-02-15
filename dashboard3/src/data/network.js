// Pipe network topology with sensor metadata per pipe.

const nodes = {
  Compressor: { x: 100, y: 400, label: 'Compressor' },
  ManifoldA:  { x: 340, y: 240, label: 'Manifold A' },
  ManifoldB:  { x: 340, y: 560, label: 'Manifold B' },
  ZoneA1:     { x: 620, y: 140, label: 'Zone A-1' },
  ZoneA2:     { x: 620, y: 340, label: 'Zone A-2' },
  ZoneB1:     { x: 620, y: 480, label: 'Zone B-1' },
  ZoneB2:     { x: 620, y: 660, label: 'Zone B-2' },
  Collector:  { x: 870, y: 400, label: 'Collector' },
  Return:     { x: 1080, y: 400, label: 'Return' },
};

const pipes = [
  { id: 'P-001', label: 'Feed A',   start: 'Compressor', end: 'ManifoldA' },
  { id: 'P-002', label: 'Feed B',   start: 'Compressor', end: 'ManifoldB' },
  { id: 'P-003', label: 'Line A1',  start: 'ManifoldA',  end: 'ZoneA1' },
  { id: 'P-004', label: 'Line A2',  start: 'ManifoldA',  end: 'ZoneA2' },
  { id: 'P-005', label: 'Line B1',  start: 'ManifoldB',  end: 'ZoneB1' },
  { id: 'P-006', label: 'Line B2',  start: 'ManifoldB',  end: 'ZoneB2' },
  { id: 'P-007', label: 'Ret A',    start: 'ZoneA1',     end: 'Collector' },
  { id: 'P-008', label: 'Ret A2',   start: 'ZoneA2',     end: 'Collector' },
  { id: 'P-009', label: 'Ret B1',   start: 'ZoneB1',     end: 'Collector' },
  { id: 'P-010', label: 'Main Ret', start: 'Collector',  end: 'Return' },
];

const valvePipes = ['P-003', 'P-005', 'P-009', 'P-010'];
const valves = valvePipes.map((pid) => {
  const pipe = pipes.find((p) => p.id === pid);
  const s = nodes[pipe.start];
  const e = nodes[pipe.end];
  return { id: `V-${pid}`, x: (s.x + e.x) / 2, y: (s.y + e.y) / 2 };
});

export const network = { nodes, pipes, valves };

// ---------- sensor simulation helpers ----------

function jitter(range) {
  return (Math.random() - 0.5) * 2 * range;
}

/** Normal sensor reading for a pipe */
function normalReading(pipeIndex) {
  const basePressure = 114.9 - pipeIndex * 0.3;
  return {
    pressureIn:  +(basePressure + jitter(1.5)).toFixed(2),
    pressureOut: +(basePressure - 1.0 + jitter(1.2)).toFixed(2),
    temperature: +(22.7 + jitter(1.0)).toFixed(2),
    humidity:    +(45.7 + jitter(1.5)).toFixed(2),
  };
}

/** Anomalous sensor reading (simulates leak) */
function anomalyReading(pipeIndex) {
  const basePressure = 114.9 - pipeIndex * 0.3;
  const drop = 15 + Math.random() * 10;
  return {
    pressureIn:  +(basePressure + jitter(2.0)).toFixed(2),
    pressureOut: +(basePressure - drop + jitter(3.0)).toFixed(2),
    temperature: +(27.7 + jitter(2.5)).toFixed(2),
    humidity:    +(33.7 + jitter(4.0)).toFixed(2),
  };
}

/** Generate one tick of sensor data for every pipe */
export function generateTick(anomalyPipeIds = new Set()) {
  const ts = Date.now();
  const readings = {};
  pipes.forEach((pipe, idx) => {
    const fn = anomalyPipeIds.has(pipe.id) ? anomalyReading : normalReading;
    readings[pipe.id] = { ...fn(idx), ts };
  });
  return readings;
}
