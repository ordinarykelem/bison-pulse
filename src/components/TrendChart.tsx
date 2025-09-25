import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import { BisonDetection } from '../types';
import { Card } from './ui/card';

interface TrendChartProps {
  data: BisonDetection[];
}

export default function TrendChart({ data }: TrendChartProps) {
  const chartData = data.map(detection => ({
    ...detection,
    time: format(new Date(detection.timestamp), 'HH:mm:ss'),
    fullTime: new Date(detection.timestamp).toLocaleTimeString()
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-elevated">
          <p className="text-sm font-medium text-foreground">
            Time: {data.fullTime}
          </p>
          <p className="text-sm text-muted-foreground">
            Count: <span className="font-medium text-primary">{data.count} bison</span>
          </p>
          <p className="text-sm text-muted-foreground">
            Movement: <span className="font-medium">{data.movement}</span>
          </p>
          <p className="text-sm text-muted-foreground">
            FPS: <span className="font-medium">{data.fps}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="shadow-card">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-foreground">
            Bison Count Trend
          </h3>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <div className="w-3 h-3 bg-primary rounded-full" />
            <span>Live count</span>
          </div>
        </div>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="hsl(var(--border))"
                opacity={0.5}
              />
              <XAxis 
                dataKey="time" 
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                domain={['dataMin - 1', 'dataMax + 1']}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line 
                type="monotone" 
                dataKey="count" 
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: 'hsl(var(--primary))', strokeWidth: 2 }}
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 text-center text-sm text-muted-foreground">
          Showing last {data.length} data points (rolling 15-30 minutes)
        </div>
      </div>
    </Card>
  );
}