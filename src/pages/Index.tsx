import { useBisonStream } from '../hooks/useBisonStream';
import HeaderStatus from '../components/HeaderStatus';
import KpiCards from '../components/KpiCards';
import TrendChart from '../components/TrendChart';
import RecentEventsTable from '../components/RecentEventsTable';
import SystemOverview from '../components/SystemOverview';
import UAVStatus from '../components/UAVStatus';
import GroundRobotStatus from '../components/GroundRobotStatus';
import AlertsPanel from '../components/AlertsPanel';
import LiveVideoFeed from '../components/LiveVideoFeed';

const Index = () => {
  const { detections, status, kpiData, systemStatus } = useBisonStream();

  return (
    <div className="min-h-screen bg-background">
      <HeaderStatus status={status} />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* System Overview */}
        <SystemOverview systemStatus={systemStatus} />
        
        {/* Live Video and KPIs Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="xl:col-span-2">
            <LiveVideoFeed isLive={status.isLive} />
          </div>
          <div>
            <KpiCards data={kpiData} />
          </div>
        </div>
        
        {/* Fleet Status Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          <UAVStatus uavs={systemStatus.uavs} />
          <GroundRobotStatus robots={systemStatus.groundRobots} />
        </div>
        
        {/* Alerts Panel */}
        <AlertsPanel alerts={systemStatus.alerts} />
        
        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <TrendChart data={detections} />
          <RecentEventsTable data={detections} />
        </div>
      </main>
    </div>
  );
};

export default Index;
