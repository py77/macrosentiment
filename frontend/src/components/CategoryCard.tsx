import SparkLine from './SparkLine';
import type { CategorySummary } from '../types/macro';

interface CategoryCardProps {
  category: CategorySummary;
}

const SIGNAL_COLORS: Record<string, string> = {
  bullish: '#a6e3a1',
  bearish: '#f38ba8',
  neutral: '#7f849c',
};

const SIGNAL_ARROWS: Record<string, string> = {
  bullish: '\u25b2',
  bearish: '\u25bc',
  neutral: '\u25c6',
};

const CATEGORY_LABELS: Record<string, string> = {
  rates: 'RATES & YIELD CURVE',
  inflation: 'INFLATION',
  growth: 'GROWTH & ACTIVITY',
  labor: 'LABOR MARKET',
  sentiment: 'MARKET SENTIMENT',
  credit: 'CREDIT & CONDITIONS',
  liquidity: 'LIQUIDITY',
  global: 'GLOBAL / CROSS-ASSET',
  equity: 'EQUITY MARKET',
};

export default function CategoryCard({ category }: CategoryCardProps) {
  const signalColor = SIGNAL_COLORS[category.signal];
  const label = CATEGORY_LABELS[category.name] || category.name.toUpperCase();

  return (
    <div
      className="rounded border p-3 space-y-2"
      style={{ background: '#181825', borderColor: '#313244' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-[0.65rem] font-semibold tracking-wider" style={{ color: '#7f849c' }}>
          {label}
        </span>
        <span className="text-xs font-bold" style={{ color: signalColor }}>
          {SIGNAL_ARROWS[category.signal]}{' '}
          {category.signal.toUpperCase()}
        </span>
      </div>

      {/* Score */}
      <div className="text-xs" style={{ color: '#585b70' }}>
        z-score:{' '}
        <span
          className="tabular-nums"
          style={{ color: category.score > 0.5 ? '#a6e3a1' : category.score < -0.5 ? '#f38ba8' : '#bac2de' }}
        >
          {category.score > 0 ? '+' : ''}
          {category.score.toFixed(2)}
        </span>
      </div>

      {/* Key indicators */}
      <div className="space-y-1">
        {category.key_indicators.map((ind) => (
          <div key={ind.series_id} className="flex items-center justify-between text-xs gap-2">
            <span className="truncate" style={{ color: '#bac2de', maxWidth: '40%' }}>
              {ind.name}
            </span>
            <div className="flex items-center gap-2">
              <span className="tabular-nums" style={{ color: '#cdd6f4' }}>
                {ind.latest_value !== null ? ind.latest_value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '--'}
              </span>
              {ind.change_1d !== null && (
                <span
                  className="tabular-nums text-[0.65rem]"
                  style={{ color: ind.change_1d >= 0 ? '#a6e3a1' : '#f38ba8' }}
                >
                  {ind.change_1d >= 0 ? '+' : ''}
                  {ind.change_1d.toFixed(2)}
                </span>
              )}
              <SparkLine data={ind.sparkline} width={50} height={18} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
