import { useEffect, useRef, useState, useCallback } from 'react';
import { network } from '../data/network';

const HISTORY_SIZE = 60;          // keep last 60 data points
const WS_URL       = 'ws://localhost:8000/ws';
const RECONNECT_MS = 2000;

/**
 * useSensorStream – connects to the Python backend via WebSocket.
 *
 * The backend runs:
 *   data_generator → isolation forest model → WebSocket broadcast
 *
 * Each message is JSON:
 *   { timestamp, readings: { [pipeId]: { pressureIn, pressureOut, temperature, humidity, ts } },
 *     anomalies: ["P-001", ...], scores: { [pipeId]: float } }
 *
 * Returns:
 *  latest        – latest readings keyed by pipe ID
 *  history       – { [pipeId]: [ ...last 60 readings ] }
 *  anomalyPipes  – Set of pipe IDs the model flagged as anomalies
 *  scores        – { [pipeId]: anomaly_score }
 *  connected     – whether WebSocket is live
 */
export function useSensorStream() {
  const [latest, setLatest]         = useState({});
  const [history, setHistory]       = useState(() => {
    const h = {};
    network.pipes.forEach((p) => (h[p.id] = []));
    return h;
  });
  const [anomalyPipes, setAnomalyPipes] = useState(() => new Set());
  const [scores, setScores]             = useState({});
  const [connected, setConnected]       = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    let alive = true;
    let reconnectTimer = null;

    function connect() {
      if (!alive) return;
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WS] connected');
        setConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          const { readings, anomalies, scores: sc } = msg;

          setLatest(readings);
          setAnomalyPipes(new Set(anomalies));
          setScores(sc ?? {});

          setHistory((prev) => {
            const next = {};
            for (const pipeId of Object.keys(prev)) {
              if (readings[pipeId]) {
                const arr = [...prev[pipeId], readings[pipeId]];
                next[pipeId] = arr.length > HISTORY_SIZE ? arr.slice(-HISTORY_SIZE) : arr;
              } else {
                next[pipeId] = prev[pipeId];
              }
            }
            return next;
          });
        } catch (err) {
          console.warn('[WS] bad message', err);
        }
      };

      ws.onclose = () => {
        console.log('[WS] disconnected, retrying…');
        setConnected(false);
        if (alive) reconnectTimer = setTimeout(connect, RECONNECT_MS);
      };

      ws.onerror = () => ws.close();
    }

    connect();

    return () => {
      alive = false;
      clearTimeout(reconnectTimer);
      wsRef.current?.close();
    };
  }, []);

  // toggleAnomaly is kept as no-op for API compat (anomalies come from the model now)
  const toggleAnomaly = useCallback(() => {}, []);

  return { latest, history, anomalyPipes, scores, connected, toggleAnomaly };
}
