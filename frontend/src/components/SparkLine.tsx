import { LineChart, Line, ResponsiveContainer } from 'recharts';

interface SparkLineProps {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
}

export default function SparkLine({ data, color = '#7f849c', width = 80, height = 24 }: SparkLineProps) {
  if (!data || data.length < 2) return <span className="text-neutral-600">--</span>;

  const chartData = data.map((v, i) => ({ i, v }));
  const isUp = data[data.length - 1] >= data[0];
  const lineColor = color !== '#7f849c' ? color : isUp ? '#a6e3a1' : '#f38ba8';

  return (
    <div style={{ width, height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <Line
            type="monotone"
            dataKey="v"
            stroke={lineColor}
            dot={false}
            strokeWidth={1.2}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
