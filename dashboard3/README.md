# Dashboard3 (React + Vite)

A 2.5D-style pipe network UI with leak highlighting. Built with React, Tailwind, Framer Motion.

## Run locally
```bash
cd dashboard3
npm install
npm run dev    # http://localhost:5173
```

## Features
- Pipe network (2.5D shading) with valves and labels
- Leak selection: pipe turns hot red, pulsing leak marker
- KPIs: pressure, flow, leak probability, timestamp
- Pressure sparkline with animated cursor
- Simulated acoustic spectrogram grid

## Notes
- Data is simulated; wire real APIs by replacing the mock generators in `src/App.jsx`.
- Adjust layout/geometry in `src/data/network.js`.
