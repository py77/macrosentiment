import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ReferenceArea,
  ReferenceLine,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { RegimeOut } from '../types/macro';

interface RegimeQuadrantProps {
  current: RegimeOut | null;
  history?: RegimeOut[];
}

const REGIME_COLORS: Record<string, string> = {
  goldilocks: 'rgba(166, 227, 161, 0.08)',
  reflation: 'rgba(249, 226, 175, 0.08)',
  deflation: 'rgba(137, 180, 250, 0.08)',
  stagflation: 'rgba(243, 139, 168, 0.08)',
};

const DOT_COLORS: Record<string, string> = {
  goldilocks: '#a6e3a1',
  reflation: '#f9e2af',
  deflation: '#89b4fa',
  stagflation: '#f38ba8',
};

export default function RegimeQuadrant({ current, history = [] }: RegimeQuadrantProps) {
  // Trail: last 30 data points + current
  const trail = history.slice(-30).map((r) => ({
    x: r.growth_score,
    y: r.inflation_score,
    regime: r.regime,
    date: r.date,
  }));

  const currentPoint = current
    ? [{ x: current.growth_score, y: current.inflation_score, regime: current.regime, date: current.date }]
    : [];

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 10 }}>
          {/* Quadrant backgrounds */}
          <ReferenceArea x1={0} x2={1} y1={-1} y2={0} fill={REGIME_COLORS.goldilocks} />
          <ReferenceArea x1={0} x2={1} y1={0} y2={1} fill={REGIME_COLORS.reflation} />
          <ReferenceArea x1={-1} x2={0} y1={-1} y2={0} fill={REGIME_COLORS.deflation} />
          <ReferenceArea x1={-1} x2={0} y1={0} y2={1} fill={REGIME_COLORS.stagflation} />

          <XAxis
            type="number"
            dataKey="x"
            domain={[-1, 1]}
            tickCount={5}
            tick={{ fill: '#7f849c', fontSize: 10 }}
            label={{ value: 'Growth', position: 'bottom', fill: '#7f849c', fontSize: 10 }}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={[-1, 1]}
            tickCount={5}
            tick={{ fill: '#7f849c', fontSize: 10 }}
            label={{ value: 'Inflation', angle: -90, position: 'left', fill: '#7f849c', fontSize: 10 }}
          />

          <ReferenceLine x={0} stroke="#313244" strokeDasharray="3 3" />
          <ReferenceLine y={0} stroke="#313244" strokeDasharray="3 3" />

          <Tooltip
            contentStyle={{ background: '#181825', border: '1px solid #313244', fontSize: '0.7rem' }}
            labelStyle={{ color: '#cdd6f4' }}
            formatter={(value: number | undefined) => (value ?? 0).toFixed(3)}
          />

          {/* Historical trail */}
          <Scatter
            data={trail}
            fill="#585b70"
            fillOpacity={0.4}
            r={2}
            isAnimationActive={false}
          />

          {/* Current position */}
          <Scatter
            data={currentPoint}
            fill={current ? DOT_COLORS[current.regime] : '#cdd6f4'}
            r={6}
            stroke="#cdd6f4"
            strokeWidth={1}
          />
        </ScatterChart>
      </ResponsiveContainer>
      {/* Quadrant labels */}
      <div className="relative -mt-[15.5rem] pointer-events-none text-[0.6rem] font-medium">
        <span className="absolute left-[60%] top-2 regime-goldilocks opacity-50">GOLDILOCKS</span>
        <span className="absolute right-[5%] top-2 regime-reflation opacity-50">REFLATION</span>
        <span className="absolute left-[5%] bottom-8 regime-deflation opacity-50">DEFLATION</span>
        <span className="absolute left-[5%] top-2 regime-stagflation opacity-50">STAGFLATION</span>
      </div>
    </div>
  );
}
