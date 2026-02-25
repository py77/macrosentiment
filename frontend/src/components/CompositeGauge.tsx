import SentimentBar from './SentimentBar';
import type { RegimeOut } from '../types/macro';

interface CompositeGaugeProps {
  regime: RegimeOut | null;
  compositeScore: number;
  categoryScores?: Record<string, number>;
}

const REGIME_DISPLAY: Record<string, { label: string; color: string }> = {
  goldilocks: { label: 'GOLDILOCKS', color: '#a6e3a1' },
  reflation: { label: 'REFLATION', color: '#f9e2af' },
  deflation: { label: 'DEFLATION', color: '#89b4fa' },
  stagflation: { label: 'STAGFLATION', color: '#f38ba8' },
};

function scoreColor(score: number): string {
  if (score >= 30) return '#a6e3a1';
  if (score >= 0) return '#f9e2af';
  if (score >= -30) return '#fab387';
  return '#f38ba8';
}

export default function CompositeGauge({ regime, compositeScore, categoryScores }: CompositeGaugeProps) {
  const display = regime ? REGIME_DISPLAY[regime.regime] : null;

  return (
    <div className="space-y-4">
      {/* Score display */}
      <div className="text-center">
        <div
          className="text-5xl font-bold tabular-nums"
          style={{ color: scoreColor(compositeScore) }}
        >
          {compositeScore >= 0 ? '+' : ''}
          {compositeScore.toFixed(1)}
        </div>
        <div className="text-xs mt-1" style={{ color: '#7f849c' }}>
          COMPOSITE SCORE
        </div>
      </div>

      {/* Regime badge */}
      {display && (
        <div className="flex justify-center">
          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold border regime-bg-${regime!.regime}`}
            style={{ color: display.color }}
          >
            {display.label}
          </span>
        </div>
      )}

      {/* Sentiment bar */}
      <SentimentBar score={compositeScore} />

      {/* Component breakdown */}
      {categoryScores && Object.keys(categoryScores).length > 0 && (
        <div className="space-y-1 mt-3">
          <div className="text-[0.6rem] uppercase tracking-wider" style={{ color: '#585b70' }}>
            Components
          </div>
          {Object.entries(categoryScores)
            .sort(([, a], [, b]) => b - a)
            .map(([cat, score]) => (
              <div key={cat} className="flex items-center justify-between text-xs">
                <span style={{ color: '#7f849c' }}>{cat}</span>
                <span
                  className="tabular-nums"
                  style={{ color: score > 0.5 ? '#a6e3a1' : score < -0.5 ? '#f38ba8' : '#bac2de' }}
                >
                  {score > 0 ? '+' : ''}
                  {score.toFixed(2)}
                </span>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
