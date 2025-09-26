# Bison Pulse - Real-time Bison Tracking System

A professional, responsive analytics dashboard for monitoring bison populations in real-time. Built with React, TypeScript, Tailwind CSS, and Recharts.

## Features

- **Real-time Data Streaming**: Server-Sent Events (SSE) with automatic fallback to REST polling
- **Live Analytics**: KPI cards showing current count, averages, FPS, and connection status
- **Interactive Charts**: Real-time line chart with 15-30 minute rolling window
- **Event History**: Table of recent detections with movement tracking
- **Responsive Design**: Mobile-first design that works on all devices
- **Mock Data Mode**: Built-in mock data generator for development without backend
- **Professional UI**: Earth-toned design system inspired by wildlife monitoring

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS with custom design system
- **Charts**: Recharts for data visualization
- **HTTP Client**: Native Fetch API
- **Date Handling**: date-fns for time formatting
- **Icons**: Custom icons for wildlife theme

## Data Contract

The dashboard expects data from a FastAPI backend with this JSON structure:

```json
{
  "timestamp": "2025-09-23T16:20:00Z",
  "count": 5,
  "movement": "north",   // "north" | "south" | "east" | "west" | "stationary"
  "fps": 24.8,
  "source": "rtsp"       // "rtsp" | "sample"
}
```

## Configuration

### Environment Variables

Create a `.env.local` file based on `.env.example`:

```bash
# Copy the example file
cp .env.example .env.local
```

Then configure your backend URLs:

```env
# Base API URL for REST endpoints
VITE_API_URL=http://localhost:8000

# Server-Sent Events stream URL  
VITE_STREAM_URL=http://localhost:8000/metrics/stream

# Optional: Force mock data mode
VITE_USE_MOCK_DATA=false
```

### Backend API Endpoints

The dashboard expects these endpoints from your FastAPI backend:

- `GET /metrics/latest` - Latest detection data
- `GET /metrics/window?minutes=15` - Historical data for time window
- `GET /metrics/stream` - Server-Sent Events stream (EventSource)

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- (Optional) FastAPI backend running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:8080`

### Running Modes

#### With Backend (Production Mode)
1. Ensure your FastAPI backend is running on `http://localhost:8000`
2. Configure `.env.local` with correct URLs
3. Start the dashboard - it will connect via SSE or polling

#### Mock Data Mode (Development)
1. Leave `.env.local` unconfigured or set invalid URLs
2. The dashboard automatically falls back to mock data
3. Generates realistic bison tracking data every 1-2 seconds

## Dashboard Components

### Header Status
- Live connection indicator (SSE/Polling/Offline)
- Last update timestamp with relative time
- Connection type display

### KPI Cards
- **Current Count**: Latest bison count
- **Average (15 min)**: Rolling 15-minute average
- **Frame Rate**: Current FPS from video source
- **Data Source**: Connection status indicator

### Trend Chart
- Real-time line chart of bison count over time
- Interactive tooltips with detailed information
- Automatic scaling and smooth animations
- Rolling 15-30 minute window (max 1,800 data points)

### Recent Events Table
- Last 20 detection events in reverse chronological order
- Movement direction indicators with arrow symbols
- Source type badges (RTSP/Sample)
- Responsive table design

## Design System

The dashboard uses a custom wildlife monitoring theme:

- **Colors**: Earth tones (warm browns, forest greens, golden accents)
- **Typography**: System fonts with monospace for data
- **Layout**: Card-based design with consistent spacing
- **Animations**: Smooth transitions and live data indicators

## Data Flow

1. **SSE Connection**: Dashboard attempts to connect to `/metrics/stream`
2. **Fallback to Polling**: If SSE fails, polls `/metrics/latest` every 2 seconds
3. **Mock Data**: If no backend available, generates realistic mock data
4. **Data Processing**: Maintains rolling buffer of 1,800 points (30 minutes)
5. **Real-time Updates**: All components update automatically with new data

## Deployment

### Build and Deploy

```bash
# Build the project
npm run build

# Preview production build locally
npm run preview
```

Deploy the `dist` folder to your preferred hosting service (Netlify, Vercel, etc.)

### Environment Variables

Set these in your hosting dashboard:
- `VITE_API_URL`: Your production API URL
- `VITE_STREAM_URL`: Your production SSE endpoint

## Testing

The dashboard includes built-in error handling and graceful degradation:

- **Connection Failures**: Automatic fallback from SSE to polling to mock data
- **Data Validation**: Handles missing or malformed data gracefully
- **Responsive Testing**: Works across desktop, tablet, and mobile viewports
- **Performance**: Efficient data management with automatic cleanup of old data points

## Troubleshooting

### Common Issues

**Dashboard shows "Offline" status:**
- Check that your backend is running and accessible
- Verify environment variables in `.env.local`
- Check browser console for connection errors

**Charts not updating:**
- Ensure data is being received (check Network tab)
- Verify data format matches expected contract
- Check for JavaScript errors in console

**Mock data not working:**
- Clear browser cache and reload
- Check that no environment variables are set
- Verify mock data generation in browser console

### Debug Mode

Add `?debug=true` to the URL to enable debug logging in the browser console.

## License

This project is licensed under the MIT License.

---

Built for wildlife conservation and monitoring.