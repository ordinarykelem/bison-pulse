import { KPIData } from '../types';
import { Card } from './ui/card';

interface KpiCardsProps {
  data: KPIData;
}

export default function KpiCards({ data }: KpiCardsProps) {
  const kpis = [
    {
      title: 'Current Count',
      value: data.currentCount,
      unit: 'bison',
      icon: '🦬',
      gradient: 'bg-gradient-primary'
    },
    {
      title: 'Average (15 min)',
      value: data.averageCount.toFixed(1),
      unit: 'avg',
      icon: '📊',
      gradient: 'bg-gradient-secondary'
    },
    {
      title: 'Frame Rate',
      value: data.fps.toFixed(1),
      unit: 'fps',
      icon: '📹',
      gradient: 'bg-gradient-primary'
    },
    {
      title: 'Data Source',
      value: data.lastUpdate ? 'Active' : 'Inactive',
      unit: '',
      icon: '📡',
      gradient: 'bg-gradient-secondary'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {kpis.map((kpi, index) => (
        <Card 
          key={index} 
          className="relative overflow-hidden shadow-card hover:shadow-elevated transition-smooth"
        >
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-muted-foreground">
                  {kpi.title}
                </p>
                <div className="flex items-baseline space-x-2 mt-2">
                  <p className="text-2xl font-bold text-foreground">
                    {kpi.value}
                  </p>
                  {kpi.unit && (
                    <p className="text-sm font-medium text-muted-foreground">
                      {kpi.unit}
                    </p>
                  )}
                </div>
              </div>
              <div className={`w-12 h-12 rounded-lg ${kpi.gradient} flex items-center justify-center shadow-sm`}>
                <span className="text-lg">{kpi.icon}</span>
              </div>
            </div>
          </div>
          
          {/* Subtle animated background pattern */}
          <div className="absolute inset-0 bg-gradient-chart opacity-30 pointer-events-none" />
        </Card>
      ))}
    </div>
  );
}