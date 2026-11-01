import React from 'react';
import { Video } from 'lucide-react';

function ClipLibrary() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Clip Library</h2>
        <p className="text-gray-400">Browse and manage your generated clips</p>
      </div>

      <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
        <Video size={48} className="mx-auto mb-4 text-gray-500" />
        <p className="text-gray-400 text-lg">No clips in library</p>
        <p className="text-gray-500 text-sm mt-2">Generated clips will appear here</p>
      </div>
    </div>
  );
}

export default ClipLibrary;
