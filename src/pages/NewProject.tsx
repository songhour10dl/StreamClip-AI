import React, { useState } from 'react';
import { Link, AlertCircle, CheckCircle, Loader } from 'lucide-react';

interface VideoInfo {
  title: string;
  duration: number;
  uploader: string;
}

function NewProject() {
  const [url, setUrl] = useState('');
  const [platform, setPlatform] = useState<'twitch' | 'kick' | null>(null);
  const [status, setStatus] = useState<'idle' | 'validating' | 'valid' | 'invalid' | 'processing'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);

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
    setVideoInfo(null);
    
    if (inputUrl) {
      detectPlatform(inputUrl);
    } else {
      setPlatform(null);
    }
  };

  const handleValidate = async () => {
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
    
    try {
      const response = await fetch('http://localhost:8000/api/projects/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.valid) {
        setStatus('valid');
        setVideoInfo({
          title: data.info.title,
          duration: data.info.duration,
          uploader: data.info.uploader || 'Unknown',
        });
      } else {
        setStatus('invalid');
        setErrorMessage(data.message || 'Invalid URL or video not accessible');
      }
    } catch (error) {
      setStatus('invalid');
      setErrorMessage('Failed to connect to backend. Is the server running on port 8000?');
    }
  };

  const handleStartAnalysis = async () => {
    if (!platform) return;
    
    setStatus('processing');
    
    try {
      const response = await fetch('http://localhost:8000/api/projects/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url,
          platform,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert(`Project created! ID: ${data.id}\n\nProcessing started. Check the Processing Queue to monitor progress.`);
        // Reset form
        setUrl('');
        setPlatform(null);
        setStatus('idle');
        setVideoInfo(null);
      } else {
        setStatus('invalid');
        setErrorMessage('Failed to create project');
      }
    } catch (error) {
      setStatus('invalid');
      setErrorMessage('Failed to start processing. Check backend connection.');
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  return (
    <div className="p-8 overflow-y-auto h-full">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">New Project</h2>
        <p className="text-gray-400">Create a new clip generation project from a VOD or clip URL</p>
      </div>

      <div className="max-w-3xl">
        {/* URL Input */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <label className="block text-sm font-medium mb-2">Video URL</label>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={url}
                onChange={handleUrlChange}
                placeholder="https://www.twitch.tv/videos/... or https://kick.com/..."
                className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 pr-20 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
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
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors whitespace-nowrap"
            >
              {status === 'validating' ? 'Validating...' : 'Validate'}
            </button>
          </div>

          {/* Status Messages */}
          {status === 'invalid' && (
            <div className="mt-3 flex items-start gap-2 text-red-400 text-sm">
              <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
              <span className="break-words">{errorMessage}</span>
            </div>
          )}
          {status === 'valid' && (
            <div className="mt-3 flex items-center gap-2 text-green-400 text-sm">
              <CheckCircle size={16} className="flex-shrink-0" />
              <span>URL is valid and ready to process</span>
            </div>
          )}
        </div>

        {/* Video Preview */}
        {status === 'valid' && videoInfo && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
            <h3 className="text-lg font-semibold mb-4">Video Information</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-start gap-4">
                <span className="text-gray-400 whitespace-nowrap">Platform:</span>
                <span className="font-medium capitalize text-right">{platform}</span>
              </div>
              <div className="flex justify-between items-start gap-4">
                <span className="text-gray-400 whitespace-nowrap">Title:</span>
                <span className="font-medium text-right break-words max-w-xs">{videoInfo.title}</span>
              </div>
              <div className="flex justify-between items-start gap-4">
                <span className="text-gray-400 whitespace-nowrap">Duration:</span>
                <span className="font-medium text-right">{formatDuration(videoInfo.duration)}</span>
              </div>
              <div className="flex justify-between items-start gap-4">
                <span className="text-gray-400 whitespace-nowrap">Uploader:</span>
                <span className="font-medium text-right break-words max-w-xs">{videoInfo.uploader}</span>
              </div>
              <div className="flex justify-between items-start gap-4">
                <span className="text-gray-400 whitespace-nowrap">Status:</span>
                <span className="font-medium text-green-400 text-right">Available</span>
              </div>
            </div>
          </div>
        )}

        {/* Supported Platforms */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <h3 className="text-lg font-semibold mb-4">Supported Platforms</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg">
              <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <Link size={20} />
              </div>
              <div className="min-w-0">
                <div className="font-medium">Twitch</div>
                <div className="text-xs text-gray-400">VODs & Clips</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg">
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <Link size={20} />
              </div>
              <div className="min-w-0">
                <div className="font-medium">Kick</div>
                <div className="text-xs text-gray-400">VODs & Clips</div>
              </div>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-4 leading-relaxed">
            Only process content you have permission to download and republish. Respect platform restrictions and copyright.
          </p>
        </div>

        {/* Start Button */}
        {status === 'valid' && (
          <button
            onClick={handleStartAnalysis}
            disabled={status === 'processing'}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed py-4 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center gap-2"
          >
            {status === 'processing' ? (
              <>
                <Loader className="animate-spin" size={20} />
                Starting Analysis...
              </>
            ) : (
              <>
                <Loader size={20} />
                Start Analysis
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}

export default NewProject;
