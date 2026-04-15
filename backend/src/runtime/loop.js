import { withStore } from '../data/store.js';
import { runAgents } from '../agents/index.js';
import { summarizeMetrics } from '../services/revenueEngine.js';

export const startRuntimeLoop = () => {
  const intervalMs = 15000;

  setInterval(() => {
    withStore((store) => {
      const opportunities = runAgents(store.opportunities);
      const metrics = summarizeMetrics(opportunities);

      const historyEntry = {
        capturedAt: new Date().toISOString(),
        ...metrics
      };

      return {
        ...store,
        opportunities,
        metricsHistory: [...store.metricsHistory.slice(-99), historyEntry]
      };
    });
  }, intervalMs);
};
