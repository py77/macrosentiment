import { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { useIndicatorHistory } from '../hooks/useMacro';

interface HistoryChartProps {
  seriesId: string;
}

export default function HistoryChart({ seriesId }: HistoryChartProps) {
  const [range, setRange] = useState<'1Y' | '2Y' | '5Y'>('1Y');
  const { data, isLoading } = useIndicatorHistory(seriesId);

  if (isLoading) {
    return <div className="text-xs" style={{ color: '#585b70' }}>Loading...</div>;
  }

  if (!data || data.values.length === 0) {
    return <div className="text-xs" style={{ color: '#585b70' }}>No history available</div>;
  }

  // Filter by range
  const now = new Date();
  const rangeMap: Record<string, number> = { '1Y': 365, '2Y': 730, '5Y': 1825 };
  const cutoff = new Date(now.getTime() - rangeMap[range] * 24 * 60 * 60 * 1000);
  const filtered = data.values.filter((v) => new Date(v.date) >= cutoff);

  return (
    <div className="space-y-2 p-2 rounded" style={{ background: '#11111b' }}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium" style={{ color: '#cdd6f4' }}>
          {data.name}
        </span>
        <div className="flex gap-1">
          {(['1Y', '2Y', '5Y'] as const).map((r) => (
            <button
              key={r}
              className="px-2 py-0.5 text-[0.6rem] rounded border"
              style={{
                background: range === r ? '#313244' : 'transparent',
                borderColor: '#313244',
                color: range === r ? '#cdd6f4' : '#585b70',
              }}
              onClick={() => setRange(r)}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={filtered} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
          <XAxis
            dataKey="date"
            tick={{ fill: '#585b70', fontSize: 9 }}
            tickFormatter={(d) => {
              const dt = new Date(d);
              return `${dt.getMonth() + 1}/${dt.getFullYear().toString().slice(2)}`;
            }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: '#585b70', fontSize: 9 }}
            width={50}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{
              background: '#181825',
              border: '1px solid #313244',
              fontSize: '0.7rem',
              color: '#cdd6f4',
            }}
            labelFormatter={(d) => new Date(d).toLocaleDateString()}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#89b4fa"
            dot={false}
            strokeWidth={1.5}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
