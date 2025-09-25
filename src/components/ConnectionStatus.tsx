import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { StreamStatus } from '../types';
import { Wifi, WifiOff, RefreshCw, Server } from 'lucide-react';

interface ConnectionStatusProps {
  status: StreamStatus;
  onReconnect?: () => void;
}

const ConnectionStatus = ({ status, onReconnect }: ConnectionStatusProps) => {
  const getConnectionIcon = () => {
    if (status.isLive) {
      return <Wifi className="h-4 w-4 text-green-500" />;
    }
    return <WifiOff className="h-4 w-4 text-red-500" />;
  };

  const getConnectionTypeLabel = () => {
    switch (status.connectionType) {
      case 'sse': return 'Server-Sent Events';
      case 'polling': return 'HTTP Polling';
      case 'offline': return 'Offline';
      default: return 'Unknown';
    }
  };

  const getStatusColor = () => {
    if (status.isLive) return 'bg-green-500';
    return 'bg-red-500';
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Server className="h-4 w-4" />
          Python Backend Connection
        </CardTitle>
        <div className="flex items-center gap-2">
          <Badge className={`${getStatusColor()} text-white`}>
            {status.isLive ? 'CONNECTED' : 'DISCONNECTED'}
          </Badge>
          {onReconnect && (
            <Button size="sm" variant="outline" onClick={onReconnect}>
              <RefreshCw className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="flex items-center gap-2">
            {getConnectionIcon()}
            Connection Type:
          </span>
          <span className="font-medium">{getConnectionTypeLabel()}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span>Last Update:</span>
          <span className="font-medium">
            {status.lastUpdate 
              ? new Date(status.lastUpdate).toLocaleTimeString()
              : 'Never'
            }
          </span>
        </div>
        
        <div className="text-xs text-muted-foreground">
          <p>Backend URL: http://localhost:8080</p>
          <p>Expected endpoints: /api/latest, /api/history, /stream</p>
          {!status.isLive && (
            <p className="text-orange-500 mt-2">
              ⚠️ Make sure your Python bison tracker is running on port 8080
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ConnectionStatus;