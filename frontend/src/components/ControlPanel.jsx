import { useState } from 'react';

export default function ControlPanel({ addOpportunity, addDraft }) {
  const [opportunity, setOpportunity] = useState({
    role: '',
    company: '',
    salary: 180000,
    equity: 10000,
    probability: 0.2
  });

  const submitOpportunity = async (event) => {
    event.preventDefault();
    await addOpportunity(opportunity);
    setOpportunity({ role: '', company: '', salary: 180000, equity: 10000, probability: 0.2 });
  };

  const createEmailDraft = async () => {
    await addDraft({
      type: 'gmail',
      subject: 'Follow-up on opportunity',
      body: 'Draft generated for review. Human-in-the-loop approval required before sending.',
      relatedOpportunityId: null
    });
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <form onSubmit={submitOpportunity} className="bg-slate-900 border border-slate-700 rounded-xl p-4 space-y-3">
        <h2 className="font-medium">Add Opportunity</h2>
        <input className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2" placeholder="Role" value={opportunity.role} onChange={(e) => setOpportunity((p) => ({ ...p, role: e.target.value }))} required />
        <input className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2" placeholder="Company" value={opportunity.company} onChange={(e) => setOpportunity((p) => ({ ...p, company: e.target.value }))} required />
        <button className="bg-emerald-500 text-slate-900 px-3 py-2 rounded font-semibold" type="submit">Add</button>
      </form>

      <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 space-y-3">
        <h2 className="font-medium">Execution Console</h2>
        <p className="text-sm text-slate-400">Generate Gmail/LinkedIn/Calendar artifacts for manual review.</p>
        <button onClick={createEmailDraft} className="bg-sky-500 text-slate-900 px-3 py-2 rounded font-semibold">Create Gmail Draft</button>
      </div>
    </div>
  );
}
