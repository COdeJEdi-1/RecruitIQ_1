export type CallStatus = 'calling' | 'completed' | 'queued' | 'retry' | 'failed';

export interface DashboardStats {
  totalCandidates: number;
  completedCalls: number;
  activeCalls: number;
  pendingCalls: number;
  failedCalls: number;
  qualifiedCandidates: number;
}

export interface Candidate {
  id: string;
  name: string;
  phone: string;
  phoneNormalized?: string;
  status: CallStatus;
  duration: string;
  retry: number;
  requestId?: number;
  dispatchFailed?: boolean;
}

export interface CandidateResult {
  id: string;
  name: string;
  experience: string;
  currentCtc: string;
  expectedCtc: string;
  noticePeriod: string;
  currentLocation: string;
  preferredLocation: string;
  shift: string;
  jobChange: string;
  result: string;
  status: CallStatus;
}

export interface Campaign {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'paused' | 'draft';
  createdBy: string;
  startedAt: string;
  totalCandidates: number;
  completed: number;
  running: number;
  queued: number;
  retries: number;
  averageDuration: string;
  progress: number;
}

export interface ParsedCandidate {
  id: string;
  name: string;
  phone: string;
  email: string;
  phoneNormalized: string | null;
  raw: Record<string, string>;
}

export interface UploadedFile {
  name: string;
  candidatesFound: number;
  validated: boolean;
  candidates: ParsedCandidate[];
  columns: string[];
  invalidPhoneCount: number;
}

export interface AnalyticsMetrics {
  answered: number;
  busy: number;
  rejected: number;
  voicemail: number;
  qualified: number;
  rejectedCandidates: number;
}

export interface CampaignReportSummary {
  totalCandidates: number;
  completedCalls: number;
  failedCalls: number;
  activeCalls: number;
  pendingCalls: number;
  qualifiedCandidates: number;
  campaignProgress: number;
  createdBy: string;
  startedAt: string;
}

export interface CampaignReportCandidateRow {
  name: string;
  phone: string;
  status: CallStatus;
}

export interface CampaignReport {
  id: string;
  name: string;
  campaignId: string;
  campaignName: string;
  date: string;
  completedAt: string;
  candidates: number;
  status: 'ready' | 'processing';
  summary: CampaignReportSummary;
  candidateRows: CampaignReportCandidateRow[];
  results: CandidateResult[];
}
