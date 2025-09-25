import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { GroundRobot as GroundRobotType } from '../types';
import { Bot, Battery, Signal, Target, MapPin } from 'lucide-react';

interface GroundRobotStatusProps {
  robots: GroundRobotType[];
}

const GroundRobotStatus = ({ robots }: GroundRobotStatusProps) => {
  const getStatusColor = (status: GroundRobotType['status']) => {
    switch (status) {
      case 'deployed': return 'bg-green-500';
      case 'returning': return 'bg-blue-500';
      case 'charging': return 'bg-yellow-500';
      case 'maintenance': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getTaskColor = (task: GroundRobotType['task']) => {
    switch (task) {
      case 'herding': return 'bg-orange-500';
      case 'monitoring': return 'bg-blue-500';
      case 'guidance': return 'bg-green-500';
      case 'standby': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="h-5 w-5" />
          Ground Robot Fleet
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {robots.map((robot) => (
            <Card key={robot.id} className="border-2">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{robot.name}</h4>
                  <Badge 
                    className={`${getStatusColor(robot.status)} text-white`}
                  >
                    {robot.status}
                  </Badge>
                </div>
                <Badge 
                  variant="outline" 
                  className={`${getTaskColor(robot.task)} text-white w-fit`}
                >
                  {robot.task}
                </Badge>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <Battery className="h-4 w-4" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Battery</span>
                      <span>{robot.batteryLevel}%</span>
                    </div>
                    <Progress value={robot.batteryLevel} className="h-2" />
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Signal className="h-4 w-4" />
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Signal</span>
                      <span>{robot.signalStrength}%</span>
                    </div>
                    <Progress value={robot.signalStrength} className="h-2" />
                  </div>
                </div>
                
                {robot.targetBison && (
                  <div className="flex items-center gap-2 text-sm">
                    <Target className="h-4 w-4" />
                    <span>Target: Bison #{robot.targetBison}</span>
                  </div>
                )}
                
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MapPin className="h-4 w-4" />
                  <span>{robot.position.lat.toFixed(4)}, {robot.position.lng.toFixed(4)}</span>
                </div>
                
                <div className="text-xs text-muted-foreground">
                  Last update: {new Date(robot.lastUpdate).toLocaleTimeString()}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default GroundRobotStatus;