import React from 'react';
import { Play } from 'lucide-react';

function VideoPreview() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Video Preview</h2>
        <p className="text-gray-400">Preview your clips before exporting</p>
      </div>

      <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
        <Play size={48} className="mx-auto mb-4 text-gray-500" />
        <p className="text-gray-400 text-lg">No video selected</p>
        <p className="text-gray-500 text-sm mt-2">Select a clip to preview it</p>
      </div>
    </div>
  );
}

export default VideoPreview;
