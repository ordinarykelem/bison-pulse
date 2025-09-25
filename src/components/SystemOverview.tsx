import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { SystemStatus } from '../types';
import { Shield, Wifi, Cloud, Server, Activity } from 'lucide-react';

interface SystemOverviewProps {
  systemStatus: SystemStatus;
}

const SystemOverview = ({ systemStatus }: SystemOverviewProps) => {
  const getOperationalModeColor = (mode: SystemStatus['operationalMode']) => {
    switch (mode) {
      case 'normal': return 'bg-green-500';
      case 'alert': return 'bg-yellow-500';
      case 'emergency': return 'bg-red-500';
      case 'maintenance': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getNetworkQualityColor = (quality: string) => {
    switch (quality) {
      case 'excellent': return 'text-green-500';
      case 'good': return 'text-blue-500';
      case 'poor': return 'text-yellow-500';
      case 'critical': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const activeUAVs = systemStatus.uavs.filter(uav => uav.status === 'active').length;
  const deployedRobots = systemStatus.groundRobots.filter(robot => robot.status === 'deployed').length;
  const activeAlerts = systemStatus.alerts.filter(alert => !alert.resolved).length;

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          System Overview
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Operational Status */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              <span className="font-medium">Status</span>
            </div>
            <Badge 
              className={`${getOperationalModeColor(systemStatus.operationalMode)} text-white`}
            >
              {systemStatus.operationalMode.toUpperCase()}
            </Badge>
          </div>

          {/* Fleet Status */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              <span className="font-medium">Fleet</span>
            </div>
            <div className="space-y-1 text-sm">
              <div>UAVs Active: {activeUAVs}/{systemStatus.uavs.length}</div>
              <div>Robots Deployed: {deployedRobots}/{systemStatus.groundRobots.length}</div>
            </div>
          </div>

          {/* Network Status */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Wifi className="h-4 w-4" />
              <span className="font-medium">Network</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <Server className={`h-3 w-3 ${systemStatus.networkStatus.edgeProcessing ? 'text-green-500' : 'text-red-500'}`} />
                <span>Edge: {systemStatus.networkStatus.edgeProcessing ? 'Online' : 'Offline'}</span>
              </div>
              <div className="flex items-center gap-2">
                <Cloud className={`h-3 w-3 ${systemStatus.networkStatus.cloudConnection ? 'text-green-500' : 'text-red-500'}`} />
                <span>Cloud: {systemStatus.networkStatus.cloudConnection ? 'Connected' : 'Disconnected'}</span>
              </div>
              <div className={`${getNetworkQualityColor(systemStatus.networkStatus.communicationQuality)}`}>
                Quality: {systemStatus.networkStatus.communicationQuality}
              </div>
            </div>
          </div>

          {/* Alert Summary */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              <span className="font-medium">Alerts</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <div className={`h-2 w-2 rounded-full ${activeAlerts > 0 ? 'bg-red-500' : 'bg-green-500'}`} />
                <span>{activeAlerts} Active Alerts</span>
              </div>
              <div className="text-muted-foreground">
                Last sync: {new Date(systemStatus.networkStatus.lastSync).toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>

        {/* System Health Bar */}
        <div className="mt-6 p-4 bg-muted rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="font-medium">System Health</span>
            <span className="text-sm">
              {systemStatus.operationalMode === 'normal' ? '98%' : 
               systemStatus.operationalMode === 'alert' ? '85%' :
               systemStatus.operationalMode === 'emergency' ? '65%' : '45%'}
            </span>
          </div>
          <div className="w-full bg-background rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                systemStatus.operationalMode === 'normal' ? 'bg-green-500 w-[98%]' :
                systemStatus.operationalMode === 'alert' ? 'bg-yellow-500 w-[85%]' :
                systemStatus.operationalMode === 'emergency' ? 'bg-red-500 w-[65%]' : 'bg-blue-500 w-[45%]'
              }`}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SystemOverview;