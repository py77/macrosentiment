import { useState } from 'react';
import SparkLine from './SparkLine';
import HistoryChart from './HistoryChart';
import type { IndicatorOut } from '../types/macro';

interface IndicatorTableProps {
  indicators: IndicatorOut[];
}

const SIGNAL_COLORS: Record<string, string> = {
  bullish: '#a6e3a1',
  bearish: '#f38ba8',
  neutral: '#7f849c',
};

function formatValue(value: number | null, unit: string): string {
  if (value === null) return '--';
  if (Math.abs(value) >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (Math.abs(value) >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function zScoreBar(z: number | null): React.ReactNode {
  if (z === null) return '--';
  const width = Math.min(Math.abs(z) * 25, 50);
  const color = z > 0.5 ? '#a6e3a1' : z < -0.5 ? '#f38ba8' : '#585b70';
  return (
    <div className="flex items-center gap-1">
      <span className="tabular-nums text-xs" style={{ color, minWidth: '3rem', textAlign: 'right' }}>
        {z > 0 ? '+' : ''}
        {z.toFixed(2)}
      </span>
      <div className="relative h-1.5 w-12 rounded-full overflow-hidden" style={{ background: '#313244' }}>
        <div
          className="absolute top-0 h-full rounded-full"
          style={{
            left: z >= 0 ? '50%' : `${50 - width}%`,
            width: `${width}%`,
            background: color,
          }}
        />
      </div>
    </div>
  );
}

export default function IndicatorTable({ indicators }: IndicatorTableProps) {
  const [expanded, setExpanded] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);

  const categories = [...new Set(indicators.map((i) => i.category))];
  const filtered = categoryFilter
    ? indicators.filter((i) => i.category === categoryFilter)
    : indicators;

  return (
    <div>
      {/* Filter tabs */}
      <div className="flex gap-2 mb-2 flex-wrap">
        <button
          className="px-2 py-0.5 text-[0.65rem] rounded border"
          style={{
            background: !categoryFilter ? '#313244' : 'transparent',
            borderColor: '#313244',
            color: !categoryFilter ? '#cdd6f4' : '#585b70',
          }}
          onClick={() => setCategoryFilter(null)}
        >
          ALL
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            className="px-2 py-0.5 text-[0.65rem] rounded border"
            style={{
              background: categoryFilter === cat ? '#313244' : 'transparent',
              borderColor: '#313244',
              color: categoryFilter === cat ? '#cdd6f4' : '#585b70',
            }}
            onClick={() => setCategoryFilter(cat === categoryFilter ? null : cat)}
          >
            {cat.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ textAlign: 'left' }}>Name</th>
              <th>Category</th>
              <th>Latest</th>
              <th>1D</th>
              <th>1W</th>
              <th>1M</th>
              <th>Z-Score</th>
              <th>Pctl</th>
              <th>Signal</th>
              <th>30d</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((ind) => (
              <>
                <tr
                  key={ind.series_id}
                  className="cursor-pointer"
                  onClick={() => setExpanded(expanded === ind.series_id ? null : ind.series_id)}
                >
                  <td style={{ textAlign: 'left', color: '#cdd6f4' }}>{ind.name}</td>
                  <td style={{ color: '#585b70' }}>{ind.category}</td>
                  <td className="tabular-nums">{formatValue(ind.latest_value, ind.unit)}</td>
                  <td style={{ color: (ind.change_1d ?? 0) >= 0 ? '#a6e3a1' : '#f38ba8' }}>
                    {ind.change_1d !== null ? `${ind.change_1d >= 0 ? '+' : ''}${ind.change_1d.toFixed(2)}` : '--'}
                  </td>
                  <td style={{ color: (ind.change_1w ?? 0) >= 0 ? '#a6e3a1' : '#f38ba8' }}>
                    {ind.change_1w !== null ? `${ind.change_1w >= 0 ? '+' : ''}${ind.change_1w.toFixed(2)}` : '--'}
                  </td>
                  <td style={{ color: (ind.change_1m ?? 0) >= 0 ? '#a6e3a1' : '#f38ba8' }}>
                    {ind.change_1m !== null ? `${ind.change_1m >= 0 ? '+' : ''}${ind.change_1m.toFixed(2)}` : '--'}
                  </td>
                  <td>{zScoreBar(ind.z_score)}</td>
                  <td className="tabular-nums" style={{ color: '#bac2de' }}>
                    {ind.percentile !== null ? `${ind.percentile.toFixed(0)}%` : '--'}
                  </td>
                  <td>
                    <span style={{ color: SIGNAL_COLORS[ind.signal || 'neutral'] }}>
                      {(ind.signal || 'neutral').toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <SparkLine data={ind.sparkline} width={60} height={18} />
                  </td>
                </tr>
                {expanded === ind.series_id && (
                  <tr key={`${ind.series_id}-detail`}>
                    <td colSpan={10} style={{ padding: '8px 0' }}>
                      <HistoryChart seriesId={ind.series_id} />
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
