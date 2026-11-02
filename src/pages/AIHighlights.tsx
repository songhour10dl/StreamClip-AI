import React, { useEffect, useState } from 'react';
import { Sparkles, Clock, TrendingUp } from 'lucide-react';

interface Highlight {
  id: string;
  project_id: string;
  start: number;
  end: number;
  reason: string | null;
  category: string | null;
  score: number | null;
  status: string;
  export_path: string | null;
  thumbnail: string | null;
  created_at: string;
}

interface Project {
  id: string;
  name: string;
  file_path: string;
}

function AIHighlights() {
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch projects on mount
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/projects/');
        if (response.ok) {
          const data = await response.json();
          setProjects(data);
          // Auto-select first project if available
          if (data.length > 0) {
            setSelectedProject(data[0].id);
          }
        }
      } catch (err) {
        console.error('Failed to fetch projects:', err);
        setError('Failed to load projects');
      }
    };
    fetchProjects();
  }, []);

  // Fetch highlights when project selected
  useEffect(() => {
    if (!selectedProject) {
      setLoading(false);
      return;
    }

    const fetchHighlights = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`http://localhost:8000/api/highlights/?project_id=${selectedProject}`);
        if (response.ok) {
          const data = await response.json();
          // Sort by score (highest first)
          const sorted = data.sort((a: Highlight, b: Highlight) => 
            (b.score || 0) - (a.score || 0)
          );
          setHighlights(sorted);
        } else {
          setError('Failed to load highlights');
        }
      } catch (err) {
        console.error('Failed to fetch highlights:', err);
        setError('Failed to load highlights');
      } finally {
        setLoading(false);
      }
    };
    fetchHighlights();
  }, [selectedProject]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getDuration = (start: number, end: number): string => {
    const duration = end - start;
    return `${duration.toFixed(1)}s`;
  };

  const getScoreColor = (score: number | null): string => {
    if (!score) return 'bg-gray-600';
    if (score >= 0.8) return 'bg-green-600';
    if (score >= 0.6) return 'bg-blue-600';
    if (score >= 0.4) return 'bg-yellow-600';
    return 'bg-orange-600';
  };

  const getScoreLabel = (score: number | null): string => {
    if (!score) return 'N/A';
    return (score * 100).toFixed(0);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">AI Highlights</h2>
        <p className="text-gray-400">Automatically detected highlights from your videos</p>
      </div>

      {/* Project Selector */}
      {projects.length > 0 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Select Project
          </label>
          <select
            value={selectedProject || ''}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-full max-w-md"
          >
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-6">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading highlights...</p>
        </div>
      ) : highlights.length === 0 ? (
        /* Empty State */
        <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
          <Sparkles size={48} className="mx-auto mb-4 text-gray-500" />
          <p className="text-gray-400 text-lg">No highlights yet</p>
          <p className="text-gray-500 text-sm mt-2">
            {selectedProject 
              ? 'Process this video to generate AI highlights'
              : 'Select a project or process a video to generate AI highlights'}
          </p>
        </div>
      ) : (
        /* Highlights Grid */
        <>
          <div className="mb-4 text-sm text-gray-400">
            Found {highlights.length} highlight{highlights.length !== 1 ? 's' : ''}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {highlights.map((highlight) => (
              <div
                key={highlight.id}
                className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden hover:border-gray-600 transition-colors"
              >
                {/* Thumbnail */}
                {highlight.thumbnail ? (
                  <img
                    src={highlight.thumbnail}
                    alt="Highlight thumbnail"
                    className="w-full h-40 object-cover bg-gray-900"
                  />
                ) : (
                  <div className="w-full h-40 bg-gray-900 flex items-center justify-center">
                    <Sparkles size={32} className="text-gray-700" />
                  </div>
                )}

                <div className="p-4">
                  {/* Score Badge */}
                  <div className="flex items-center justify-between mb-3">
                    <div className={`${getScoreColor(highlight.score)} px-3 py-1 rounded-full flex items-center gap-1.5`}>
                      <TrendingUp size={14} />
                      <span className="text-sm font-semibold">
                        {getScoreLabel(highlight.score)}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 uppercase tracking-wide">
                      {highlight.status}
                    </span>
                  </div>

                  {/* Time Range */}
                  <div className="flex items-center gap-2 text-gray-300 mb-2">
                    <Clock size={16} />
                    <span className="text-sm font-mono">
                      {formatTime(highlight.start)} - {formatTime(highlight.end)}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({getDuration(highlight.start, highlight.end)})
                    </span>
                  </div>

                  {/* Category */}
                  {highlight.category && (
                    <div className="mb-2">
                      <span className="inline-block bg-gray-700 text-gray-300 text-xs px-2 py-1 rounded">
                        {highlight.category}
                      </span>
                    </div>
                  )}

                  {/* Reason */}
                  {highlight.reason && (
                    <p className="text-sm text-gray-400 line-clamp-2">
                      {highlight.reason}
                    </p>
                  )}

                  {/* Export Status */}
                  {highlight.export_path && (
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <p className="text-xs text-green-500 flex items-center gap-1">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        Exported
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default AIHighlights;
