const StagePill = ({ stage }) => (
  <span className="px-2 py-1 text-xs rounded-full bg-slate-800 border border-slate-600">{stage}</span>
);

export default function OpportunityTable({ opportunities = [] }) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 overflow-auto">
      <h2 className="font-medium mb-4">Pipeline Opportunities</h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-400">
            <th className="pb-2">Role</th>
            <th className="pb-2">Company</th>
            <th className="pb-2">Probability</th>
            <th className="pb-2">EV</th>
            <th className="pb-2">Stage</th>
          </tr>
        </thead>
        <tbody>
          {opportunities.map((opportunity) => (
            <tr key={opportunity.id} className="border-t border-slate-800">
              <td className="py-2">{opportunity.role}</td>
              <td className="py-2">{opportunity.company}</td>
              <td className="py-2">{Math.round(opportunity.probability * 100)}%</td>
              <td className="py-2">${opportunity.expectedValue.toLocaleString()}</td>
              <td className="py-2"><StagePill stage={opportunity.stage} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
