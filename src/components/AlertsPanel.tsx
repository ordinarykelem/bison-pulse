import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { SystemAlert } from '../types';
import { AlertTriangle, AlertCircle, Info, CheckCircle, MapPin, Clock } from 'lucide-react';

interface AlertsPanelProps {
  alerts: SystemAlert[];
  onResolveAlert?: (alertId: string) => void;
}

const AlertsPanel = ({ alerts, onResolveAlert }: AlertsPanelProps) => {
  const getSeverityIcon = (severity: SystemAlert['severity']) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'high':
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
      case 'medium':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'low':
        return <Info className="h-4 w-4 text-blue-500" />;
      default:
        return <Info className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSeverityColor = (severity: SystemAlert['severity']) => {
    switch (severity) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getTypeLabel = (type: SystemAlert['type']) => {
    switch (type) {
      case 'boundary_breach': return 'Boundary Breach';
      case 'animal_distress': return 'Animal Distress';
      case 'equipment_failure': return 'Equipment Failure';
      case 'weather_warning': return 'Weather Warning';
      default: return type;
    }
  };

  const activeAlerts = alerts.filter(alert => !alert.resolved);
  const resolvedAlerts = alerts.filter(alert => alert.resolved);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          System Alerts
          {activeAlerts.length > 0 && (
            <Badge variant="destructive" className="ml-2">
              {activeAlerts.length} Active
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Active Alerts */}
          {activeAlerts.length > 0 && (
            <div>
              <h4 className="font-medium mb-3 text-red-600">Active Alerts</h4>
              <div className="space-y-3">
                {activeAlerts.map((alert) => (
                  <Card key={alert.id} className="border-l-4 border-l-red-500">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            {getSeverityIcon(alert.severity)}
                            <Badge className={`${getSeverityColor(alert.severity)} text-white`}>
                              {alert.severity.toUpperCase()}
                            </Badge>
                            <Badge variant="outline">
                              {getTypeLabel(alert.type)}
                            </Badge>
                          </div>
                          <p className="font-medium mb-2">{alert.message}</p>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(alert.timestamp).toLocaleString()}
                            </div>
                            {alert.location && (
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                {alert.location.lat.toFixed(4)}, {alert.location.lng.toFixed(4)}
                              </div>
                            )}
                          </div>
                          {alert.assignedTo && (
                            <div className="text-sm text-muted-foreground mt-1">
                              Assigned to: {alert.assignedTo}
                            </div>
                          )}
                        </div>
                        {onResolveAlert && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => onResolveAlert(alert.id)}
                          >
                            Resolve
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Recent Resolved Alerts */}
          {resolvedAlerts.length > 0 && (
            <div>
              <h4 className="font-medium mb-3 text-green-600 flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                Recently Resolved
              </h4>
              <div className="space-y-2">
                {resolvedAlerts.slice(0, 3).map((alert) => (
                  <Card key={alert.id} className="border-l-4 border-l-green-500 opacity-75">
                    <CardContent className="p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="bg-green-50">
                          {getTypeLabel(alert.type)}
                        </Badge>
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        <span className="text-sm text-green-600">Resolved</span>
                      </div>
                      <p className="text-sm">{alert.message}</p>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(alert.timestamp).toLocaleString()}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {alerts.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-500" />
              <p>No active alerts</p>
              <p className="text-sm">All systems operating normally</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default AlertsPanel;