import React from 'react';
import { Upload } from 'lucide-react';

function ExportManager() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Export Manager</h2>
        <p className="text-gray-400">Manage and export your finished clips</p>
      </div>

      <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
        <Upload size={48} className="mx-auto mb-4 text-gray-500" />
        <p className="text-gray-400 text-lg">No exports ready</p>
        <p className="text-gray-500 text-sm mt-2">Completed clips will appear here for export</p>
      </div>
    </div>
  );
}

export default ExportManager;
