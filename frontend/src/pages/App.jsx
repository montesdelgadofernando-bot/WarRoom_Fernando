import KPIGrid from '../components/KPIGrid';
import EVChart from '../components/EVChart';
import OpportunityTable from '../components/OpportunityTable';
import ControlPanel from '../components/ControlPanel';
import { useCareerOS } from '../hooks/useCareerOS';

const AGENTS = ['scout', 'analyst', 'strategist', 'recruiter', 'negotiator'];

export default function App() {
  const { state, loading, addOpportunity, addDraft } = useCareerOS();

  if (loading || !state) {
    return <div className="min-h-screen text-slate-200 p-6">Loading CareerOS...</div>;
  }

  return (
    <main className="min-h-screen text-slate-100 p-6 bg-slate-950">
      <div className="max-w-7xl mx-auto space-y-6">
        <header className="space-y-3">
          <h1 className="text-3xl font-bold">CareerOS</h1>
          <p className="text-slate-400">Local-first multi-agent SaaS operating system for career pipeline execution.</p>
          <div className="flex gap-2 flex-wrap">
            {AGENTS.map((agent) => (
              <span key={agent} className="text-xs px-2 py-1 rounded-full bg-slate-800 border border-slate-700">{agent}</span>
            ))}
          </div>
        </header>

        <KPIGrid metrics={state.metrics} />
        <ControlPanel addOpportunity={addOpportunity} addDraft={addDraft} />
        <EVChart history={state.metricsHistory} />
        <OpportunityTable opportunities={state.opportunities} />
      </div>
    </main>
  );
}
