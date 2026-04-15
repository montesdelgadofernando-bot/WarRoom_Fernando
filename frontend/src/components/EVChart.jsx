import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function EVChart({ history = [] }) {
  const chartData = history.map((point) => ({
    time: new Date(point.capturedAt).toLocaleTimeString(),
    ev: point.totalEV
  }));

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 h-72">
      <h2 className="font-medium mb-4">Historical Expected Value</h2>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <XAxis dataKey="time" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip />
          <Area type="monotone" dataKey="ev" stroke="#34d399" fill="#064e3b" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
