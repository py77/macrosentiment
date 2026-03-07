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
  const trailRaw = history.slice(-30);
  const trail = trailRaw.map((r, i) => ({
    x: r.growth_score,
    y: r.inflation_score,
    regime: r.regime,
    date: r.date,
    opacity: 0.15 + (0.7 * (i / Math.max(trailRaw.length - 1, 1))),
    size: 2 + (2 * (i / Math.max(trailRaw.length - 1, 1))),
  }));

  const currentPoint = current
    ? [{ x: current.growth_score, y: current.inflation_score, regime: current.regime, date: current.date }]
    : [];

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 10 }}>
          {/* Quadrant backgrounds with corner labels */}
          <ReferenceArea x1={0} x2={1} y1={-1} y2={0} fill={REGIME_COLORS.goldilocks}
            label={{ value: 'GOLDILOCKS', position: 'insideBottomRight', fill: '#a6e3a1', fontSize: 9, fontWeight: 500, opacity: 0.4 }} />
          <ReferenceArea x1={0} x2={1} y1={0} y2={1} fill={REGIME_COLORS.reflation}
            label={{ value: 'REFLATION', position: 'insideTopRight', fill: '#f9e2af', fontSize: 9, fontWeight: 500, opacity: 0.4 }} />
          <ReferenceArea x1={-1} x2={0} y1={-1} y2={0} fill={REGIME_COLORS.deflation}
            label={{ value: 'DEFLATION', position: 'insideBottomLeft', fill: '#89b4fa', fontSize: 9, fontWeight: 500, opacity: 0.4 }} />
          <ReferenceArea x1={-1} x2={0} y1={0} y2={1} fill={REGIME_COLORS.stagflation}
            label={{ value: 'STAGFLATION', position: 'insideTopLeft', fill: '#f38ba8', fontSize: 9, fontWeight: 500, opacity: 0.4 }} />

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
            content={({ payload }) => {
              if (!payload?.[0]) return null;
              const d = payload[0].payload;
              return (
                <div style={{
                  background: '#313244',
                  border: '1px solid #45475a',
                  borderRadius: 4,
                  padding: '6px 10px',
                  fontSize: '0.7rem',
                  color: '#cdd6f4',
                }}>
                  {d.date && <div style={{ marginBottom: 2 }}>{d.date}</div>}
                  <div>Growth: {d.x?.toFixed(3)}</div>
                  <div>Inflation: {d.y?.toFixed(3)}</div>
                  {d.regime && <div style={{ color: DOT_COLORS[d.regime] }}>{d.regime.toUpperCase()}</div>}
                </div>
              );
            }}
          />

          {/* Historical trail */}
          <Scatter
            data={trail}
            isAnimationActive={false}
            shape={(props: any) => {
              const { cx, cy, payload } = props;
              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={payload.size}
                  fill="#585b70"
                  fillOpacity={payload.opacity}
                />
              );
            }}
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
    </div>
  );
}
