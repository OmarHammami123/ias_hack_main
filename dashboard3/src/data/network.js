const nodes = {
  Compressor: { x: 140, y: 400 },
  ManifoldA: { x: 360, y: 280 },
  ManifoldB: { x: 360, y: 520 },
  ZoneA1: { x: 640, y: 200 },
  ZoneA2: { x: 640, y: 360 },
  ZoneB1: { x: 640, y: 520 },
  ZoneB2: { x: 640, y: 680 },
  Return: { x: 980, y: 400 },
};

const pipes = [
  { id: 'Pipe_A0', label: 'Feed A', start: 'Compressor', end: 'ManifoldA' },
  { id: 'Pipe_B0', label: 'Feed B', start: 'Compressor', end: 'ManifoldB' },
  { id: 'Pipe_A1', label: 'Line A1', start: 'ManifoldA', end: 'ZoneA1' },
  { id: 'Pipe_A2', label: 'Line A2', start: 'ManifoldA', end: 'ZoneA2' },
  { id: 'Pipe_B1', label: 'Line B1', start: 'ManifoldB', end: 'ZoneB1' },
  { id: 'Pipe_B2', label: 'Line B2', start: 'ManifoldB', end: 'ZoneB2' },
  { id: 'Pipe_R1', label: 'Return A', start: 'ZoneA2', end: 'Return' },
  { id: 'Pipe_R2', label: 'Return B', start: 'ZoneB1', end: 'Return' },
];

const valves = ['Pipe_A1', 'Pipe_B1', 'Pipe_R2'].map((pid) => midpoint(pid));

export const network = {
  nodes,
  pipes,
  valves,
};

function midpoint(pipeId) {
  const pipe = pipes.find((p) => p.id === pipeId);
  const start = nodes[pipe.start];
  const end = nodes[pipe.end];
  return {
    id: pipeId,
    x: (start.x + end.x) / 2,
    y: (start.y + end.y) / 2,
  };
}
