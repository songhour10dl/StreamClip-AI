import React, { useState } from 'react';
import { Link, AlertCircle, CheckCircle, Loader } from 'lucide-react';

function NewProject() {
  const [url, setUrl] = useState('');
  const [platform, setPlatform] = useState<'twitch' | 'kick' | null>(null);
  const [status, setStatus] = useState<'idle' | 'validating' | 'valid' | 'invalid'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const detectPlatform = (inputUrl: string) => {
    if (inputUrl.includes('twitch.tv')) {
      setPlatform('twitch');
      return 'twitch';
    } else if (inputUrl.includes('kick.com')) {
      setPlatform('kick');
      return 'kick';
    } else {
      setPlatform(null);
      return null;
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputUrl = e.target.value;
    setUrl(inputUrl);
    setStatus('idle');
    setErrorMessage('');
    
    if (inputUrl) {
      detectPlatform(inputUrl);
    } else {
      setPlatform(null);
    }
  };

  const handleValidate = () => {
    if (!url) {
      setStatus('invalid');
      setErrorMessage('Please enter a URL');
      return;
    }

    if (!platform) {
      setStatus('invalid');
      setErrorMessage('Unsupported platform. Please use Twitch or Kick URLs.');
      return;
    }

    setStatus('validating');
    // TODO: Call backend to validate URL
    setTimeout(() => {
      setStatus('valid');
    }, 1000);
  };

  const handleStartAnalysis = () => {
    // TODO: Create project and start processing
    console.log('Starting analysis for:', url);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">New Project</h2>
        <p className="text-gray-400">Create a new clip generation project from a VOD or clip URL</p>
      </div>

      <div className="max-w-3xl">
        {/* URL Input */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <label className="block text-sm font-medium mb-2">Video URL</label>
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={url}
                onChange={handleUrlChange}
                placeholder="https://www.twitch.tv/videos/... or https://kick.com/..."
                className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
              />
              {platform && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  <span className={`text-xs font-semibold px-2 py-1 rounded ${
                    platform === 'twitch' ? 'bg-purple-600' : 'bg-green-600'
                  }`}>
                    {platform.toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            <button
              onClick={handleValidate}
              disabled={!url || status === 'validating'}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
            >
              {status === 'validating' ? 'Validating...' : 'Validate'}
            </button>
          </div>

          {/* Status Messages */}
          {status === 'invalid' && (
            <div className="mt-3 flex items-center gap-2 text-red-400 text-sm">
              <AlertCircle size={16} />
              <span>{errorMessage}</span>
            </div>
          )}
          {status === 'valid' && (
            <div className="mt-3 flex items-center gap-2 text-green-400 text-sm">
              <CheckCircle size={16} />
              <span>URL is valid and ready to process</span>
            </div>
          )}
        </div>

        {/* Video Preview */}
        {status === 'valid' && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
            <h3 className="text-lg font-semibold mb-4">Video Information</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Platform:</span>
                <span className="font-medium capitalize">{platform}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Title:</span>
                <span className="font-medium">Loading...</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Duration:</span>
                <span className="font-medium">Loading...</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Status:</span>
                <span className="font-medium text-green-400">Available</span>
              </div>
            </div>
          </div>
        )}

        {/* Supported Platforms */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <h3 className="text-lg font-semibold mb-4">Supported Platforms</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg">
              <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                <Link size={20} />
              </div>
              <div>
                <div className="font-medium">Twitch</div>
                <div className="text-xs text-gray-400">VODs & Clips</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg">
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <Link size={20} />
              </div>
              <div>
                <div className="font-medium">Kick</div>
                <div className="text-xs text-gray-400">VODs & Clips</div>
              </div>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-4">
            Only process content you have permission to download and republish. Respect platform restrictions and copyright.
          </p>
        </div>

        {/* Start Button */}
        {status === 'valid' && (
          <button
            onClick={handleStartAnalysis}
            className="w-full bg-purple-600 hover:bg-purple-700 py-4 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center gap-2"
          >
            <Loader className="animate-spin" size={20} />
            Start Analysis
          </button>
        )}
      </div>
    </div>
  );
}

export default NewProject;
