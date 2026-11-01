import React from 'react';
import { Sparkles } from 'lucide-react';

function AIHighlights() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">AI Highlights</h2>
        <p className="text-gray-400">Automatically detected highlights from your videos</p>
      </div>

      <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
        <Sparkles size={48} className="mx-auto mb-4 text-gray-500" />
        <p className="text-gray-400 text-lg">No highlights yet</p>
        <p className="text-gray-500 text-sm mt-2">Process a video to generate AI highlights</p>
      </div>
    </div>
  );
}

export default AIHighlights;
