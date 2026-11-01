import React from 'react';
import { Activity, CheckCircle, XCircle, Loader, Pause } from 'lucide-react';

function ProcessingQueue() {
  const jobs = []; // TODO: Fetch from backend

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
          {/* Job cards will be rendered here */}
        </div>
      )}
    </div>
  );
}

export default ProcessingQueue;
