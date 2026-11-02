import { useEffect, useState } from 'react';
import { Activity, CheckCircle, XCircle, Loader, Clock } from 'lucide-react';

interface Job {
  id: string;
  project_id: string;
  status: string;
  progress: number;
  current_step: string | null;
  error: string | null;
  started_at: string;
  completed_at: string | null;
}

function ProcessingQueue() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/queue/');
        if (response.ok) {
          const data = await response.json();
          setJobs(data);
        }
      } catch (err) {
        console.error('Failed to fetch jobs:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
    const interval = setInterval(fetchJobs, 3000); // Poll every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'failed':
        return <XCircle className="text-red-500" size={20} />;
      case 'processing':
        return <Loader className="text-blue-500 animate-spin" size={20} />;
      case 'pending':
        return <Clock className="text-yellow-500" size={20} />;
      default:
        return <Activity className="text-gray-500" size={20} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/50';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'processing':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/50';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Processing Queue</h2>
          <p className="text-gray-400">Monitor active and queued video processing jobs</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
          <Loader size={48} className="mx-auto mb-4 text-gray-500 animate-spin" />
          <p className="text-gray-400 text-lg">Loading jobs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Processing Queue</h2>
        <p className="text-gray-400">Monitor active and queued video processing jobs</p>
      </div>

      {jobs.length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
          <Activity size={48} className="mx-auto mb-4 text-gray-500" />
          <p className="text-gray-400 text-lg">No processing jobs</p>
          <p className="text-gray-500 text-sm mt-2">Jobs will appear here when you start a new project</p>
        </div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getStatusIcon(job.status)}
                  <div>
                    <h3 className="text-lg font-semibold">Project: {job.project_id}</h3>
                    <p className="text-sm text-gray-400">Job ID: {job.id}</p>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                    job.status
                  )}`}
                >
                  {job.status.toUpperCase()}
                </span>
              </div>

              {job.current_step && (
                <div className="mb-3">
                  <p className="text-sm text-gray-300">
                    <span className="font-medium">Current Step:</span> {job.current_step}
                  </p>
                </div>
              )}

              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Progress</span>
                  <span className="text-gray-300">{job.progress}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              </div>

              {job.error && (
                <div className="mb-3 p-3 bg-red-500/10 border border-red-500/50 rounded">
                  <p className="text-sm text-red-400">
                    <span className="font-medium">Error:</span> {job.error}
                  </p>
                </div>
              )}

              <div className="flex gap-4 text-xs text-gray-500">
                <div>
                  <span className="font-medium">Started:</span> {formatTimestamp(job.started_at)}
                </div>
                {job.completed_at && (
                  <div>
                    <span className="font-medium">Completed:</span>{' '}
                    {formatTimestamp(job.completed_at)}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ProcessingQueue;