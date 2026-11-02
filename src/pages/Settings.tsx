import React, { useState, useEffect } from 'react';
import { Save, HardDrive, Cpu, Monitor, CheckCircle, XCircle, Loader2 } from 'lucide-react';

function SettingsPage() {
  const [settings, setSettings] = useState({
    defaultClipDuration: 60,
    minHighlightScore: 70,
    maxClips: 10,
    outputResolution: '1080x1920',
    videoQuality: 'high',
    processingMode: 'cpu',
    maxRamUsage: 8,
    storageLocation: 'C:\\StreamClipAI\\Projects',
    autoCleanup: false,
    aiModel: 'qwen:3b',
    language: 'auto',
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/settings/');
        if (response.ok) {
          const data = await response.json();
          // Parse and merge with defaults
          setSettings(prev => ({
            ...prev,
            ...data
          }));
        }
      } catch (err) {
        console.error('Failed to load settings:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveStatus('idle');
    try {
      const response = await fetch('http://localhost:8000/api/settings/', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
      
      if (!response.ok) throw new Error('Failed to save settings');
      
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
      setSaveStatus('error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-64">
        <Loader2 className="animate-spin text-purple-500" size={40} />
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Settings</h2>
        <p className="text-gray-400">Configure application preferences and processing options</p>
      </div>

      <div className="max-w-4xl space-y-6">
        {/* Processing Settings */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Cpu size={20} />
            Processing Settings
          </h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Processing Mode</label>
                <select
                  value={settings.processingMode}
                  onChange={(e) => setSettings({ ...settings, processingMode: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                >
                  <option value="cpu">CPU Only</option>
                  <option value="gpu">GPU (CUDA)</option>
                  <option value="auto">Auto Detect</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Max RAM Usage (GB)</label>
                <input
                  type="number"
                  value={settings.maxRamUsage}
                  onChange={(e) => setSettings({ ...settings, maxRamUsage: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                  min="2"
                  max="16"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">AI Model</label>
              <select
                value={settings.aiModel}
                onChange={(e) => setSettings({ ...settings, aiModel: e.target.value })}
                className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
              >
                <option value="qwen:3b">Qwen 3B (Recommended)</option>
                <option value="llama3:8b">Llama 3 8B</option>
                <option value="mistral:7b">Mistral 7B</option>
              </select>
            </div>
          </div>
        </div>

        {/* Clip Settings */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Monitor size={20} />
            Clip Settings
          </h3>
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Default Clip Duration (s)</label>
                <input
                  type="number"
                  value={settings.defaultClipDuration}
                  onChange={(e) => setSettings({ ...settings, defaultClipDuration: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                  min="15"
                  max="180"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Min Highlight Score</label>
                <input
                  type="number"
                  value={settings.minHighlightScore}
                  onChange={(e) => setSettings({ ...settings, minHighlightScore: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                  min="0"
                  max="100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Max Clips</label>
                <input
                  type="number"
                  value={settings.maxClips}
                  onChange={(e) => setSettings({ ...settings, maxClips: parseInt(e.target.value) })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                  min="1"
                  max="50"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Output Resolution</label>
                <select
                  value={settings.outputResolution}
                  onChange={(e) => setSettings({ ...settings, outputResolution: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                >
                  <option value="1080x1920">1080x1920 (9:16)</option>
                  <option value="720x1280">720x1280 (9:16)</option>
                  <option value="1920x1080">1920x1080 (16:9)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Video Quality</label>
                <select
                  value={settings.videoQuality}
                  onChange={(e) => setSettings({ ...settings, videoQuality: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                >
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Storage Settings */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <HardDrive size={20} />
            Storage Settings
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Storage Location</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={settings.storageLocation}
                  onChange={(e) => setSettings({ ...settings, storageLocation: e.target.value })}
                  className="flex-1 bg-gray-900 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500"
                />
                <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg">
                  Browse
                </button>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="autoCleanup"
                checked={settings.autoCleanup}
                onChange={(e) => setSettings({ ...settings, autoCleanup: e.target.checked })}
                className="w-4 h-4"
              />
              <label htmlFor="autoCleanup" className="text-sm">
                Automatically cleanup temporary files after processing
              </label>
            </div>
          </div>
        </div>

        {/* Save Button with Status */}
        <div className="space-y-2">
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2"
          >
            {saving ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                Saving...
              </>
            ) : (
              <>
                <Save size={20} />
                Save Settings
              </>
            )}
          </button>
          
          {saveStatus === 'success' && (
            <div className="flex items-center justify-center gap-2 text-green-500 bg-green-500/10 py-2 rounded-lg">
              <CheckCircle size={20} />
              <span>Settings saved successfully</span>
            </div>
          )}
          
          {saveStatus === 'error' && (
            <div className="flex items-center justify-center gap-2 text-red-500 bg-red-500/10 py-2 rounded-lg">
              <XCircle size={20} />
              <span>Failed to save settings. Please try again.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;