import React, { useEffect, useState } from 'react';
import {
  FolderOpen,
  Video,
  Sparkles,
  Activity,
  HardDrive,
  Clock,
} from 'lucide-react';

interface StatCard {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
}

interface DashboardStats {
  total_projects: number;
  videos_processed: number;
  highlights_generated: number;
  processing_jobs: number;
  storage_usage_gb: number;
}

function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/projects/stats/dashboard');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const statCards: StatCard[] = [
    {
      label: 'Total Projects',
      value: stats?.total_projects ?? 0,
      icon: <FolderOpen size={24} />,
      color: 'bg-blue-500',
    },
    {
      label: 'Videos Processed',
      value: stats?.videos_processed ?? 0,
      icon: <Video size={24} />,
      color: 'bg-green-500',
    },
    {
      label: 'Highlights Generated',
      value: stats?.highlights_generated ?? 0,
      icon: <Sparkles size={24} />,
      color: 'bg-purple-500',
    },
    {
      label: 'Processing Jobs',
      value: stats?.processing_jobs ?? 0,
      icon: <Activity size={24} />,
      color: 'bg-orange-500',
    },
    {
      label: 'Storage Usage',
      value: `${stats?.storage_usage_gb?.toFixed(2) ?? 0} GB`,
      icon: <HardDrive size={24} />,
      color: 'bg-red-500',
    },
  ];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Dashboard</h2>
        <p className="text-gray-400">Overview of your clip generation activity</p>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-500/10 border border-red-500 rounded-lg p-4 mb-6">
          <p className="text-red-500">Error loading dashboard stats: {error}</p>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-8">
        {statCards.map((stat, index) => (
          <div
            key={index}
            className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.color} p-3 rounded-lg`}>{stat.icon}</div>
            </div>
            <div className="text-3xl font-bold mb-1">
              {loading ? (
                <span className="text-gray-500">...</span>
              ) : (
                stat.value
              )}
            </div>
            <div className="text-sm text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Recent Projects */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">Recent Projects</h3>
          <Clock size={20} className="text-gray-400" />
        </div>
        <div className="text-center py-12 text-gray-400">
          <FolderOpen size={48} className="mx-auto mb-4 opacity-50" />
          <p>No projects yet</p>
          <p className="text-sm mt-2">Create a new project to get started</p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;