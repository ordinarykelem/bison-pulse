import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { UAVStatus as UAVStatusType } from '../types';
import { Plane, Battery, Signal, MapPin } from 'lucide-react';

interface UAVStatusProps {
  uavs: UAVStatusType[];
}

const UAVStatus = ({ uavs }: UAVStatusProps) => {
  const getStatusColor = (status: UAVStatusType['status']) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'standby': return 'bg-yellow-500';
      case 'maintenance': return 'bg-orange-500';
      case 'offline': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getMissionColor = (mission: UAVStatusType['missionType']) => {
    switch (mission) {
      case 'patrol': return 'bg-blue-500';
      case 'tracking': return 'bg-green-500';
      case 'emergency': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plane className="h-5 w-5" />
          UAV Fleet Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {uavs.map((uav) => (
            <Card key={uav.id} className="border-2">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{uav.name}</h4>
                  <Badge 
                    className={`${getStatusColor(uav.status)} text-white`}
                  >
                    {uav.status}
                  </Badge>
                </div>
                <Badge 
                  variant="outline" 
                  className={`${getMissionColor(uav.missionType)} text-white w-fit`}
                >
                  {uav.missionType}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <Battery className="h-4 w-4" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Battery</span>
                      <span>{uav.batteryLevel}%</span>
                    </div>
                    <Progress value={uav.batteryLevel} className="h-2" />
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Signal className="h-4 w-4" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Signal</span>
                      <span>{uav.signalStrength}%</span>
                    </div>
                    <Progress value={uav.signalStrength} className="h-2" />
                  </div>
                </div>
                
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MapPin className="h-4 w-4" />
                  <span>Alt: {uav.position.altitude}m</span>
                </div>
                
                <div className="text-xs text-muted-foreground">
                  Last update: {new Date(uav.lastUpdate).toLocaleTimeString()}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default UAVStatus;