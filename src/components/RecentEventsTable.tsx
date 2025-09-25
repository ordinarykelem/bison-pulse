import { format } from 'date-fns';
import { BisonDetection } from '../types';
import { Card } from './ui/card';

interface RecentEventsTableProps {
  data: BisonDetection[];
}

export default function RecentEventsTable({ data }: RecentEventsTableProps) {
  const recentData = data.slice(-20).reverse(); // Last 20 events, newest first

  const getMovementIcon = (movement: BisonDetection['movement']) => {
    switch (movement) {
      case 'north': return '⬆️';
      case 'south': return '⬇️';
      case 'east': return '➡️';
      case 'west': return '⬅️';
      default: return '⏸️';
    }
  };

  const getSourceBadge = (source: BisonDetection['source']) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium";
    if (source === 'rtsp') {
      return `${baseClasses} bg-live/10 text-live border border-live/20`;
    }
    return `${baseClasses} bg-warning/10 text-warning border border-warning/20`;
  };

  return (
    <Card className="shadow-card">
      <div className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-6">
          Recent Events
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                  Time
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                  Count
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                  Movement
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                  FPS
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                  Source
                </th>
              </tr>
            </thead>
            <tbody>
              {recentData.map((detection, index) => (
                <tr 
                  key={`${detection.timestamp}-${index}`}
                  className="border-b border-border/50 hover:bg-muted/30 transition-smooth"
                >
                  <td className="py-3 px-4 text-sm text-foreground font-mono">
                    {format(new Date(detection.timestamp), 'HH:mm:ss')}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-foreground">
                        {detection.count}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        bison
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <span>{getMovementIcon(detection.movement)}</span>
                      <span className="text-sm text-foreground capitalize">
                        {detection.movement}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-foreground font-mono">
                    {detection.fps.toFixed(1)}
                  </td>
                  <td className="py-3 px-4">
                    <span className={getSourceBadge(detection.source)}>
                      {detection.source.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {recentData.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <div className="mb-2">📊</div>
              <p>No recent events</p>
              <p className="text-xs">Data will appear here when tracking begins</p>
            </div>
          )}
        </div>
        
        <div className="mt-4 text-center text-sm text-muted-foreground">
          Showing last {recentData.length} events
        </div>
      </div>
    </Card>
  );
}