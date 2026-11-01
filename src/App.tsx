import React, { useState } from 'react';
import {
  Home,
  Plus,
  List,
  Sparkles,
  Video,
  Play,
  Upload,
  Settings,
} from 'lucide-react';
import Dashboard from './pages/Dashboard';
import NewProject from './pages/NewProject';
import ProcessingQueue from './pages/ProcessingQueue';
import AIHighlights from './pages/AIHighlights';
import ClipLibrary from './pages/ClipLibrary';
import VideoPreview from './pages/VideoPreview';
import ExportManager from './pages/ExportManager';
import SettingsPage from './pages/Settings';

type Page =
  | 'dashboard'
  | 'new-project'
  | 'queue'
  | 'highlights'
  | 'library'
  | 'preview'
  | 'export'
  | 'settings';

interface NavItem {
  id: Page;
  label: string;
  icon: React.ReactNode;
}

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  const navItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <Home size={20} /> },
    { id: 'new-project', label: 'New Project', icon: <Plus size={20} /> },
    { id: 'queue', label: 'Processing Queue', icon: <List size={20} /> },
    { id: 'highlights', label: 'AI Highlights', icon: <Sparkles size={20} /> },
    { id: 'library', label: 'Clip Library', icon: <Video size={20} /> },
    { id: 'preview', label: 'Video Preview', icon: <Play size={20} /> },
    { id: 'export', label: 'Export Manager', icon: <Upload size={20} /> },
    { id: 'settings', label: 'Settings', icon: <Settings size={20} /> },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'new-project':
        return <NewProject />;
      case 'queue':
        return <ProcessingQueue />;
      case 'highlights':
        return <AIHighlights />;
      case 'library':
        return <ClipLibrary />;
      case 'preview':
        return <VideoPreview />;
      case 'export':
        return <ExportManager />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold text-purple-400">StreamClip AI</h1>
          <p className="text-xs text-gray-400 mt-1">Local AI Clip Generator</p>
        </div>
        <nav className="flex-1 overflow-y-auto py-4">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-6 py-3 text-left transition-colors ${
                currentPage === item.id
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              {item.icon}
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-700 text-xs text-gray-400">
          <p>v1.0.0 - Local Processing</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
