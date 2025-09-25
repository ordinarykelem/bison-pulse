export interface BisonDetection {
  timestamp: string;
  count: number;
  movement: 'north' | 'south' | 'east' | 'west' | 'stationary';
  fps: number;
  source: 'rtsp' | 'sample';
}

export interface UAVStatus {
  id: string;
  name: string;
  status: 'active' | 'standby' | 'maintenance' | 'offline';
  batteryLevel: number;
  position: {
    lat: number;
    lng: number;
    altitude: number;
  };
  signalStrength: number;
  lastUpdate: string;
  missionType: 'patrol' | 'tracking' | 'emergency';
}

export interface GroundRobot {
  id: string;
  name: string;
  status: 'deployed' | 'returning' | 'charging' | 'maintenance';
  batteryLevel: number;
  position: {
    lat: number;
    lng: number;
  };
  targetBison: number | null;
  signalStrength: number;
  lastUpdate: string;
  task: 'herding' | 'monitoring' | 'guidance' | 'standby';
}

export interface SystemAlert {
  id: string;
  type: 'boundary_breach' | 'animal_distress' | 'equipment_failure' | 'weather_warning';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  location?: {
    lat: number;
    lng: number;
  };
  resolved: boolean;
  assignedTo?: string;
}

export interface SystemStatus {
  uavs: UAVStatus[];
  groundRobots: GroundRobot[];
  alerts: SystemAlert[];
  networkStatus: {
    edgeProcessing: boolean;
    cloudConnection: boolean;
    communicationQuality: 'excellent' | 'good' | 'poor' | 'critical';
    lastSync: string;
  };
  operationalMode: 'normal' | 'alert' | 'emergency' | 'maintenance';
}

export interface KPIData {
  currentCount: number;
  averageCount: number;
  fps: number;
  lastUpdate: string;
}

export interface StreamStatus {
  isLive: boolean;
  lastUpdate: Date | null;
  connectionType: 'sse' | 'polling' | 'offline';
}