export default function KPIGrid({ metrics }) {
  const cards = [
    { label: 'Total EV', value: `$${(metrics?.totalEV || 0).toLocaleString()}` },
    { label: 'Avg Probability', value: `${Math.round((metrics?.avgProbability || 0) * 100)}%` },
    { label: 'Opportunities', value: metrics?.opportunities || 0 }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {cards.map((card) => (
        <div key={card.label} className="rounded-xl bg-slate-900 border border-slate-700 p-4">
          <p className="text-slate-400 text-sm">{card.label}</p>
          <p className="text-2xl font-semibold mt-2 text-emerald-300">{card.value}</p>
        </div>
      ))}
    </div>
  );
}
