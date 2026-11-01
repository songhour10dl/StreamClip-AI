import React from 'react';
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

function Dashboard() {
  const stats: StatCard[] = [
    {
      label: 'Total Projects',
      value: 0,
      icon: <FolderOpen size={24} />,
      color: 'bg-blue-500',
    },
    {
      label: 'Videos Processed',
      value: 0,
      icon: <Video size={24} />,
      color: 'bg-green-500',
    },
    {
      label: 'Highlights Generated',
      value: 0,
      icon: <Sparkles size={24} />,
      color: 'bg-purple-500',
    },
    {
      label: 'Processing Jobs',
      value: 0,
      icon: <Activity size={24} />,
      color: 'bg-orange-500',
    },
    {
      label: 'Storage Usage',
      value: '0 GB',
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

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-8">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.color} p-3 rounded-lg`}>{stat.icon}</div>
            </div>
            <div className="text-3xl font-bold mb-1">{stat.value}</div>
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
