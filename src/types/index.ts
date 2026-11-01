export interface Project {
  id: string;
  url: string;
  platform: 'twitch' | 'kick';
  title: string;
  duration: number;
  thumbnail?: string;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
}

export type ProjectStatus =
  | 'waiting'
  | 'downloading'
  | 'transcribing'
  | 'analyzing'
  | 'selecting_highlights'
  | 'editing'
  | 'rendering'
  | 'completed'
  | 'failed'
  | 'cancelled';

export interface Highlight {
  id: string;
  projectId: string;
  start: number;
  end: number;
  reason: string;
  category: string;
  score: number;
  status: 'pending' | 'rendering' | 'completed' | 'failed';
  exportPath?: string;
  thumbnail?: string;
  metadata?: HighlightMetadata;
}

export interface HighlightMetadata {
  title: string;
  description: string;
  hashtags: string[];
  category: string;
}

export interface ProcessingJob {
  id: string;
  projectId: string;
  status: ProjectStatus;
  progress: number;
  currentStep: string;
  logs: string[];
  error?: string;
  startedAt: string;
  completedAt?: string;
}

export interface DashboardStats {
  totalProjects: number;
  videosProcessed: number;
  highlightsGenerated: number;
  processingJobs: number;
  storageUsed: string;
}
