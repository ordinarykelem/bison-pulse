import { useState, useEffect, useCallback, useRef } from 'react';
import { BisonDetection, StreamStatus, KPIData, SystemStatus, UAVStatus, GroundRobot, SystemAlert } from '../types';
import { BisonStreamManager } from '../lib/stream';

const MAX_DATA_POINTS = 1800; // 30 minutes at 1 point per second
const KPI_WINDOW_MINUTES = 15;

export function useBisonStream() {
  const [detections, setDetections] = useState<BisonDetection[]>([]);
  const [status, setStatus] = useState<StreamStatus>({
    isLive: false,
    lastUpdate: null,
    connectionType: 'offline'
  });
  const [kpiData, setKpiData] = useState<KPIData>({
    currentCount: 0,
    averageCount: 0,
    fps: 0,
    lastUpdate: ''
  });
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    uavs: generateMockUAVs(),
    groundRobots: generateMockRobots(),
    alerts: generateMockAlerts(),
    networkStatus: {
      edgeProcessing: true,
      cloudConnection: true,
      communicationQuality: 'excellent',
      lastSync: new Date().toISOString()
    },
    operationalMode: 'normal'
  });
  
  const streamManagerRef = useRef<BisonStreamManager | null>(null);

  const handleNewDetection = useCallback((detection: BisonDetection) => {
    setDetections(prev => {
      const updated = [...prev, detection];
      // Keep only the last MAX_DATA_POINTS
      return updated.slice(-MAX_DATA_POINTS);
    });
    
    setStatus(prev => ({
      ...prev,
      isLive: true,
      lastUpdate: new Date()
    }));
  }, []);

  const handleStatusChange = useCallback((connectionStatus: 'connected' | 'disconnected' | 'error') => {
    setStatus(prev => ({
      ...prev,
      isLive: connectionStatus === 'connected',
      connectionType: connectionStatus === 'connected' 
        ? streamManagerRef.current?.getConnectionType() || 'offline'
        : 'offline'
    }));
  }, []);

  // Calculate KPIs whenever detections change
  useEffect(() => {
    if (detections.length === 0) return;

    const latest = detections[detections.length - 1];
    const now = new Date();
    const windowStart = new Date(now.getTime() - KPI_WINDOW_MINUTES * 60 * 1000);
    
    const recentDetections = detections.filter(d => 
      new Date(d.timestamp) >= windowStart
    );
    
    const averageCount = recentDetections.length > 0
      ? recentDetections.reduce((sum, d) => sum + d.count, 0) / recentDetections.length
      : 0;

    setKpiData({
      currentCount: latest.count,
      averageCount,
      fps: latest.fps,
      lastUpdate: latest.timestamp
    });
  }, [detections]);

  // Initialize stream on mount
  useEffect(() => {
    streamManagerRef.current = new BisonStreamManager(
      handleNewDetection,
      handleStatusChange
    );

    streamManagerRef.current.start();

    return () => {
      streamManagerRef.current?.stop();
    };
  }, [handleNewDetection, handleStatusChange]);

  return {
    detections,
    status,
    kpiData,
    systemStatus,
    restart: () => {
      streamManagerRef.current?.stop();
      streamManagerRef.current?.start();
    }
  };
}

// Mock data generators
function generateMockUAVs(): UAVStatus[] {
  return [
    {
      id: 'uav-001',
      name: 'Eagle-1',
      status: 'active',
      batteryLevel: 85,
      position: { lat: 45.4215, lng: -75.6919, altitude: 120 },
      signalStrength: 92,
      lastUpdate: new Date().toISOString(),
      missionType: 'patrol'
    },
    {
      id: 'uav-002',
      name: 'Hawk-2',
      status: 'active',
      batteryLevel: 67,
      position: { lat: 45.4235, lng: -75.6899, altitude: 150 },
      signalStrength: 88,
      lastUpdate: new Date().toISOString(),
      missionType: 'tracking'
    },
    {
      id: 'uav-003',
      name: 'Falcon-3',
      status: 'standby',
      batteryLevel: 100,
      position: { lat: 45.4195, lng: -75.6939, altitude: 0 },
      signalStrength: 95,
      lastUpdate: new Date().toISOString(),
      missionType: 'patrol'
    }
  ];
}

function generateMockRobots(): GroundRobot[] {
  return [
    {
      id: 'robot-001',
      name: 'Shepherd-1',
      status: 'deployed',
      batteryLevel: 72,
      position: { lat: 45.4205, lng: -75.6929 },
      targetBison: 3,
      signalStrength: 85,
      lastUpdate: new Date().toISOString(),
      task: 'herding'
    },
    {
      id: 'robot-002',
      name: 'Guardian-2',
      status: 'deployed',
      batteryLevel: 94,
      position: { lat: 45.4225, lng: -75.6909 },
      targetBison: null,
      signalStrength: 91,
      lastUpdate: new Date().toISOString(),
      task: 'monitoring'
    }
  ];
}

function generateMockAlerts(): SystemAlert[] {
  return [
    {
      id: 'alert-001',
      type: 'boundary_breach',
      severity: 'high',
      message: 'Two bison detected 50m beyond northern boundary',
      timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      location: { lat: 45.4245, lng: -75.6889 },
      resolved: false,
      assignedTo: 'Ranger Smith'
    },
    {
      id: 'alert-002',
      type: 'equipment_failure',
      severity: 'medium',  
      message: 'UAV Falcon-3 battery degradation detected',
      timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      resolved: true,
      assignedTo: 'Tech Team'
    }
  ];
}
