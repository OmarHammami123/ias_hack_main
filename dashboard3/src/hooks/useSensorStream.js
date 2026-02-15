import { useEffect, useRef, useState, useCallback } from 'react';
import { generateTick, network } from '../data/network';

const HISTORY_SIZE = 60;          // keep last 60 seconds
const TICK_MS      = 1000;        // 1 tick / second

/**
 * useSensorStream – drives the whole dashboard.
 *
 * Returns:
 *  latest        – { [pipeId]: { pressureIn, pressureOut, temperature, humidity, ts } }
 *  history       – { [pipeId]: [ ...last 60 readings ] }
 *  anomalyPipes  – Set of pipe IDs currently anomalous
 *  toggleAnomaly – fn(pipeId) to flip anomaly state for demo purposes
 */
export function useSensorStream() {
  const [anomalySet, setAnomalySet] = useState(() => new Set());
  const [latest, setLatest]         = useState({});
  const [history, setHistory]       = useState(() => {
    const h = {};
    network.pipes.forEach((p) => (h[p.id] = []));
    return h;
  });
  const historyRef = useRef(history);
  historyRef.current = history;

  // toggle anomaly on a pipe (used by the pipe-list / demo controls)
  const toggleAnomaly = useCallback((pipeId) => {
    setAnomalySet((prev) => {
      const next = new Set(prev);
      next.has(pipeId) ? next.delete(pipeId) : next.add(pipeId);
      return next;
    });
  }, []);

  // random anomaly injection — every ~8 s flip a random pipe for realism
  const anomalyRef = useRef(anomalySet);
  anomalyRef.current = anomalySet;

  useEffect(() => {
    const id = setInterval(() => {
      const pipes = network.pipes;
      const rnd   = pipes[Math.floor(Math.random() * pipes.length)].id;
      setAnomalySet((prev) => {
        const next = new Set(prev);
        // 40 % chance to create, 60 % to clear — keeps ~1-2 active at a time
        if (next.has(rnd) || Math.random() < 0.6) next.delete(rnd);
        else next.add(rnd);
        return next;
      });
    }, 8000);
    return () => clearInterval(id);
  }, []);

  // main ticker
  useEffect(() => {
    const id = setInterval(() => {
      const tick = generateTick(anomalyRef.current);
      setLatest(tick);
      setHistory((prev) => {
        const next = {};
        for (const pipeId of Object.keys(prev)) {
          const arr = [...prev[pipeId], tick[pipeId]];
          next[pipeId] = arr.length > HISTORY_SIZE ? arr.slice(-HISTORY_SIZE) : arr;
        }
        return next;
      });
    }, TICK_MS);
    return () => clearInterval(id);
  }, []);

  return { latest, history, anomalyPipes: anomalySet, toggleAnomaly };
}
