export const computeExpectedValue = ({ salary, equity = 0, probability }) => {
  const totalValue = Number(salary || 0) + Number(equity || 0);
  return Math.round(totalValue * Number(probability || 0));
};

export const summarizeMetrics = (opportunities) => {
  const totalEV = opportunities.reduce((sum, opp) => sum + (opp.expectedValue || 0), 0);
  const avgProbability = opportunities.length
    ? opportunities.reduce((sum, opp) => sum + (opp.probability || 0), 0) / opportunities.length
    : 0;

  const stageCounts = opportunities.reduce((acc, opp) => {
    acc[opp.stage] = (acc[opp.stage] || 0) + 1;
    return acc;
  }, {});

  return {
    totalEV,
    avgProbability: Number(avgProbability.toFixed(2)),
    opportunities: opportunities.length,
    stageCounts
  };
};
