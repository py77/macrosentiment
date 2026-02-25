import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { useRegimeHistory } from '../hooks/useMacro';

const REGIME_COLORS: Record<string, string> = {
  goldilocks: '#a6e3a1',
  reflation: '#f9e2af',
  deflation: '#89b4fa',
  stagflation: '#f38ba8',
};

export default function RegimeTimeline() {
  const { data, isLoading } = useRegimeHistory();

  if (isLoading) {
    return <div className="text-xs" style={{ color: '#585b70' }}>Loading regime history...</div>;
  }

  if (!data || data.snapshots.length === 0) {
    return <div className="text-xs" style={{ color: '#585b70' }}>No regime history available</div>;
  }

  const chartData = data.snapshots.map((s) => ({
    date: s.date,
    growth: s.growth_score,
    inflation: s.inflation_score,
    composite: s.composite_score,
    regime: s.regime,
    fill: REGIME_COLORS[s.regime],
  }));

  return (
    <div className="space-y-2">
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={chartData} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="growthGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#a6e3a1" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#a6e3a1" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="inflationGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f38ba8" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#f38ba8" stopOpacity={0} />
            </linearGradient>
          </defs>

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
            domain={[-1, 1]}
            tick={{ fill: '#585b70', fontSize: 9 }}
            width={35}
          />

          <ReferenceLine y={0} stroke="#313244" strokeDasharray="3 3" />

          <Tooltip
            contentStyle={{
              background: '#181825',
              border: '1px solid #313244',
              fontSize: '0.7rem',
              color: '#cdd6f4',
            }}
            labelFormatter={(d) => new Date(d).toLocaleDateString()}
            formatter={(value: number | undefined, name: string | undefined) => [(value ?? 0).toFixed(3), name ?? '']}
          />

          <Area
            type="monotone"
            dataKey="growth"
            stroke="#a6e3a1"
            fill="url(#growthGrad)"
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="inflation"
            stroke="#f38ba8"
            fill="url(#inflationGrad)"
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="flex justify-center gap-4 text-[0.65rem]">
        <span>
          <span className="inline-block w-2 h-2 rounded-full mr-1" style={{ background: '#a6e3a1' }} />
          <span style={{ color: '#7f849c' }}>Growth Momentum</span>
        </span>
        <span>
          <span className="inline-block w-2 h-2 rounded-full mr-1" style={{ background: '#f38ba8' }} />
          <span style={{ color: '#7f849c' }}>Inflation Momentum</span>
        </span>
      </div>
    </div>
  );
}
