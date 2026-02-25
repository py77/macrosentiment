interface SentimentBarProps {
  score: number; // -100 to +100
}

export default function SentimentBar({ score }: SentimentBarProps) {
  const pct = ((score + 100) / 200) * 100;
  const clampedPct = Math.max(0, Math.min(100, pct));

  let color: string;
  if (score >= 30) color = '#a6e3a1';
  else if (score >= 0) color = '#f9e2af';
  else if (score >= -30) color = '#fab387';
  else color = '#f38ba8';

  return (
    <div className="w-full">
      <div className="relative h-2 rounded-full overflow-hidden" style={{ background: '#313244' }}>
        {/* Center line */}
        <div
          className="absolute top-0 h-full w-px"
          style={{ left: '50%', background: '#585b70' }}
        />
        {/* Fill bar */}
        <div
          className="absolute top-0 h-full rounded-full transition-all duration-500"
          style={{
            left: score >= 0 ? '50%' : `${clampedPct}%`,
            width: score >= 0 ? `${clampedPct - 50}%` : `${50 - clampedPct}%`,
            background: color,
          }}
        />
      </div>
      <div className="flex justify-between text-[0.6rem] mt-0.5" style={{ color: '#585b70' }}>
        <span>-100</span>
        <span>0</span>
        <span>+100</span>
      </div>
    </div>
  );
}
