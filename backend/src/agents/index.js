import { computeExpectedValue } from '../services/revenueEngine.js';

const nudges = {
  scout: (opp) => ({
    ...opp,
    stage: opp.stage === 'scouted' ? 'analyzed' : opp.stage,
    probability: Math.min(0.95, (opp.probability || 0.1) + 0.05)
  }),
  analyst: (opp) => ({
    ...opp,
    probability: Math.min(0.95, (opp.probability || 0.1) + 0.03)
  }),
  strategist: (opp) => ({
    ...opp,
    stage: opp.stage === 'analyzed' ? 'strategy' : opp.stage
  }),
  recruiter: (opp) => ({
    ...opp,
    stage: opp.stage === 'strategy' ? 'recruiter_contact' : opp.stage,
    probability: Math.min(0.95, (opp.probability || 0.1) + 0.02)
  }),
  negotiator: (opp) => ({
    ...opp,
    stage: opp.stage === 'offer' ? 'negotiation' : opp.stage,
    equity: Math.round((opp.equity || 0) * 1.02)
  })
};

export const runAgents = (opportunities) => {
  return opportunities.map((opportunity) => {
    const agentOrder = ['scout', 'analyst', 'strategist', 'recruiter', 'negotiator'];

    const evolved = agentOrder.reduce((current, agent) => nudges[agent](current), opportunity);

    return {
      ...evolved,
      expectedValue: computeExpectedValue(evolved),
      updatedAt: new Date().toISOString()
    };
  });
};
