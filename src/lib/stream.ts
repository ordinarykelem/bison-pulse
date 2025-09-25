import { BisonDetection } from '../types';

export type StreamCallback = (data: BisonDetection) => void;
export type StatusCallback = (status: 'connected' | 'disconnected' | 'error') => void;

export class BisonStreamManager {
  private eventSource: EventSource | null = null;
  private pollingInterval: NodeJS.Timeout | null = null;
  private onMessage: StreamCallback;
  private onStatusChange: StatusCallback;
  private streamUrl: string;
  private isUsingSSE = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;

  constructor(onMessage: StreamCallback, onStatusChange: StatusCallback) {
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
    // Update to match your Python server port and endpoint
    this.streamUrl = import.meta.env.VITE_STREAM_URL || 'http://localhost:8080/stream';
  }

  async start() {
    // Try SSE first
    try {
      await this.startSSE();
    } catch (error) {
      console.warn('SSE failed, falling back to polling:', error);
      this.startPolling();
    }
  }

  private async startSSE() {
    return new Promise<void>((resolve, reject) => {
      this.eventSource = new EventSource(this.streamUrl);
      
      const timeout = setTimeout(() => {
        this.eventSource?.close();
        reject(new Error('SSE connection timeout'));
      }, 10000); // 10 second timeout

      this.eventSource.onopen = () => {
        clearTimeout(timeout);
        this.isUsingSSE = true;
        this.reconnectAttempts = 0;
        this.onStatusChange('connected');
        resolve();
      };

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Transform your Python data format to our interface
          const detection: BisonDetection = {
            timestamp: data.timestamp || new Date().toISOString(),
            count: data.bison_count || data.count || 0,
            movement: data.movement || 'stationary',
            fps: data.fps || 0,
            source: data.source || 'rtsp'
          };
          
          this.onMessage(detection);
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
        }
      };

      this.eventSource.onerror = () => {
        clearTimeout(timeout);
        this.onStatusChange('error');
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          setTimeout(() => {
            if (this.eventSource?.readyState === EventSource.CLOSED) {
              this.startSSE().catch(() => this.startPolling());
            }
          }, 2000 * this.reconnectAttempts);
        } else {
          reject(new Error('Max SSE reconnection attempts reached'));
        }
      };
    });
  }

  private startPolling() {
    this.isUsingSSE = false;
    this.onStatusChange('connected');
    
    // Import API function dynamically to avoid circular dependency
    const pollData = async () => {
      try {
        const { getLatest } = await import('./api');
        const data = await getLatest();
        this.onMessage(data);
      } catch (error) {
        console.error('Polling failed:', error);
        this.onStatusChange('error');
      }
    };

    // Poll immediately, then every 2 seconds
    pollData();
    this.pollingInterval = setInterval(pollData, 2000);
  }

  stop() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
    
    this.onStatusChange('disconnected');
  }

  getConnectionType(): 'sse' | 'polling' | 'offline' {
    if (!this.eventSource && !this.pollingInterval) return 'offline';
    return this.isUsingSSE ? 'sse' : 'polling';
  }
}