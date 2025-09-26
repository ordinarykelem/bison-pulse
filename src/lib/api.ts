import { BisonDetection } from '../types';

// Bison Pulse API configuration
const API_BASE = import.meta.env.VITE_API_URL || 'https://bison-pulse.onrender.com';

export async function getLatest(): Promise<BisonDetection> {
  try {
    const response = await fetch(`${API_BASE}/api/latest`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    
    // Transform your Python data format to our interface
    return {
      timestamp: data.timestamp || new Date().toISOString(),
      count: data.bison_count || data.count || 0,
      movement: data.movement || 'stationary',
      fps: data.fps || 0,
      source: data.source || 'rtsp'
    };
  } catch (error) {
    console.warn('API call failed, using mock data:', error);
    return generateMockData();
  }
}

export async function getWindow(minutes = 15): Promise<BisonDetection[]> {
  try {
    const response = await fetch(`${API_BASE}/api/history?minutes=${minutes}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    
    // Transform array of detection data
    return data.map((item: any) => ({
      timestamp: item.timestamp || new Date().toISOString(),
      count: item.bison_count || item.count || 0,
      movement: item.movement || 'stationary',
      fps: item.fps || 0,
      source: item.source || 'rtsp'
    }));
  } catch (error) {
    console.warn('API call failed, using mock data:', error);
    return generateMockDataArray(minutes);
  }
}

// Get system status from your Python backend
export async function getSystemStatus() {
  try {
    const response = await fetch(`${API_BASE}/api/status`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.warn('System status API call failed:', error);
    return null;
  }
}

// Get live video stream URL
export function getVideoStreamUrl(): string {
  return `${API_BASE}/video/stream.mjpeg`;
}

// Get HLS playlist URL  
export function getHLSStreamUrl(): string {
  return `${API_BASE}/hls/index.m3u8`;
}

// Mock data generator for development
function generateMockData(): BisonDetection {
  const movements: BisonDetection['movement'][] = ['north', 'south', 'east', 'west', 'stationary'];
  const sources: BisonDetection['source'][] = ['rtsp', 'sample'];
  
  return {
    timestamp: new Date().toISOString(),
    count: Math.floor(Math.random() * 12) + 1, // 1-12 bison
    movement: movements[Math.floor(Math.random() * movements.length)],
    fps: Number((20 + Math.random() * 10).toFixed(1)), // 20-30 fps
    source: sources[Math.floor(Math.random() * sources.length)]
  };
}

function generateMockDataArray(minutes: number): BisonDetection[] {
  const data: BisonDetection[] = [];
  const now = new Date();
  const intervalMs = (minutes * 60 * 1000) / 100; // 100 data points over the time window
  
  for (let i = 99; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - (i * intervalMs));
    data.push({
      ...generateMockData(),
      timestamp: timestamp.toISOString()
    });
  }
  
  return data;
}