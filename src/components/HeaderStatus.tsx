import { formatDistanceToNow } from 'date-fns';
import { StreamStatus } from '../types';

interface HeaderStatusProps {
  status: StreamStatus;
}

export default function HeaderStatus({ status }: HeaderStatusProps) {
  const getStatusText = () => {
    switch (status.connectionType) {
      case 'sse':
        return 'Live (SSE)';
      case 'polling':
        return 'Live (Polling)';
      default:
        return 'Offline';
    }
  };

  const getStatusColor = () => {
    if (status.connectionType === 'offline') return 'bg-offline text-white';
    return 'bg-live text-white';
  };

  return (
    <header className="bg-gradient-hero border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-6">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-lg">🦬</span>
              </div>
              <h1 className="text-2xl font-bold text-foreground">
                Real-time Bison Tracking
              </h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`px-3 py-1 rounded-full text-sm font-medium transition-smooth ${getStatusColor()}`}>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${status.isLive ? 'bg-white animate-pulse' : 'bg-white/60'}`} />
                  <span>{getStatusText()}</span>
                </div>
              </div>
            </div>
            
            {status.lastUpdate && (
              <div className="text-sm text-muted-foreground">
                Last update: {formatDistanceToNow(status.lastUpdate, { addSuffix: true })}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}