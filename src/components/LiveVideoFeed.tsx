import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Video, Maximize2, RefreshCw } from 'lucide-react';
import { getVideoStreamUrl, getHLSStreamUrl } from '../lib/api';
import { useState } from 'react';

interface LiveVideoFeedProps {
  isLive: boolean;
}

const LiveVideoFeed = ({ isLive }: LiveVideoFeedProps) => {
  const [streamType, setStreamType] = useState<'mjpeg' | 'hls'>('mjpeg');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleRefresh = () => {
    // Force reload the video stream
    const video = document.getElementById('live-video') as HTMLVideoElement;
    const img = document.getElementById('live-image') as HTMLImageElement;
    
    if (streamType === 'hls' && video) {
      video.load();
    } else if (streamType === 'mjpeg' && img) {
      img.src = getVideoStreamUrl() + '?t=' + Date.now();
    }
  };

  return (
    <Card className={`w-full ${isFullscreen ? 'fixed inset-0 z-50 bg-black' : ''}`}>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Video className="h-5 w-5" />
          Live Video Feed
        </CardTitle>
        <div className="flex items-center gap-2">
          <Badge variant={isLive ? "default" : "secondary"}>
            {isLive ? 'LIVE' : 'OFFLINE'}
          </Badge>
          <div className="flex gap-1">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setStreamType(streamType === 'mjpeg' ? 'hls' : 'mjpeg')}
            >
              {streamType.toUpperCase()}
            </Button>
            <Button size="sm" variant="outline" onClick={handleRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="outline" onClick={handleFullscreen}>
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
          {streamType === 'mjpeg' ? (
            <img
              id="live-image"
              src={getVideoStreamUrl()}
              alt="Live RTSP Stream"
              className="w-full h-full object-contain"
              onError={(e) => {
                console.error('MJPEG stream error:', e);
                // Show placeholder on error
                e.currentTarget.style.display = 'none';
              }}
            />
          ) : (
            <video
              id="live-video"
              className="w-full h-full object-contain"
              controls
              autoPlay
              muted
              onError={(e) => {
                console.error('HLS stream error:', e);
              }}
            >
              <source src={getHLSStreamUrl()} type="application/x-mpegURL" />
              Your browser does not support HLS streaming.
            </video>
          )}
          
          {!isLive && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75">
              <div className="text-center text-white">
                <Video className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-lg font-medium">Stream Offline</p>
                <p className="text-sm opacity-75">Waiting for live feed...</p>
              </div>
            </div>
          )}
          
          {/* Live indicator overlay */}
          {isLive && (
            <div className="absolute top-4 left-4">
              <Badge className="bg-red-500 text-white animate-pulse">
                ● LIVE
              </Badge>
            </div>
          )}
        </div>
        
        <div className="mt-4 text-sm text-muted-foreground">
          <p>Stream URL: {streamType === 'mjpeg' ? getVideoStreamUrl() : getHLSStreamUrl()}</p>
          <p>Quality: Auto-adjusting based on network conditions</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default LiveVideoFeed;