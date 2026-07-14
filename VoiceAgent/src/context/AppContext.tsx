import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import {
  dispatchCampaignCalls,
  fetchRecentCallLogs,
  findLatestCallLog,
  getConcurrentCallLimit,
  mapOmnidimCallStatus,
  type DispatchProgressCallback,
} from '../services/omnidimension';
import type {
  Campaign,
  Candidate,
  CandidateResult,
  CallStatus,
  DashboardStats,
  UploadedFile,
  ParsedCandidate,
  CampaignReport,
} from '../types';
import {
  buildCampaignReport,
  loadStoredReports,
  saveStoredReports,
} from '../utils/generateReport';

export interface StartCampaignResult {
  success: boolean;
  dispatched: number;
  failed: number;
  error?: string;
  errors?: string[];
}

interface AppContextValue {
  dashboardStats: DashboardStats;
  campaign: Campaign;
  liveCandidates: Candidate[];
  candidateResults: CandidateResult[];
  campaignReports: CampaignReport[];
  uploadedFile: UploadedFile | null;
  isCampaignRunning: boolean;
  agentRunningSeconds: number;
  hasActiveCampaign: boolean;
  setUploadedFile: (file: UploadedFile | null) => void;
  startCampaign: (
    name: string,
    onProgress?: DispatchProgressCallback,
  ) => Promise<StartCampaignResult>;
}

const AppContext = createContext<AppContextValue | null>(null);

const emptyDashboardStats: DashboardStats = {
  totalCandidates: 0,
  completedCalls: 0,
  activeCalls: 0,
  pendingCalls: 0,
  failedCalls: 0,
  qualifiedCandidates: 0,
};

const idleCampaign: Campaign = {
  id: '—',
  name: 'No Active Campaign',
  status: 'draft',
  createdBy: '—',
  startedAt: '—',
  totalCandidates: 0,
  completed: 0,
  running: 0,
  queued: 0,
  retries: 0,
  averageDuration: '—',
  progress: 0,
};

export function formatAgentTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function buildResultFromCandidate(
  candidate: Candidate,
  parsed: ParsedCandidate | undefined,
  id: string,
): CandidateResult {
  const raw = parsed?.raw ?? {};
  const get = (...keys: string[]) => {
    for (const key of keys) {
      const match = Object.entries(raw).find(([k]) =>
        k.toLowerCase().includes(key.toLowerCase()),
      );
      if (match?.[1]) return match[1];
    }
    return '—';
  };

  return {
    id,
    name: candidate.name,
    experience: get('experience', 'exp'),
    currentCtc: get('current ctc', 'ctc', 'current salary'),
    expectedCtc: get('expected ctc', 'expected salary'),
    noticePeriod: get('notice', 'notice period'),
    currentLocation: get('current location', 'location', 'city'),
    preferredLocation: get('preferred location', 'preferred'),
    shift: get('shift'),
    jobChange: get('job change', 'open to change'),
    result: 'Completed',
    status: 'completed',
  };
}

function countByStatus(candidates: Candidate[]) {
  return {
    running: candidates.filter((c) => c.status === 'calling').length,
    queued: candidates.filter((c) => c.status === 'queued').length,
    completed: candidates.filter((c) => c.status === 'completed').length,
    failed: candidates.filter((c) => c.status === 'failed' && !c.dispatchFailed).length,
    retry: candidates.filter((c) => c.status === 'retry').length,
    dispatchFailed: candidates.filter((c) => c.dispatchFailed).length,
  };
}

interface PollUpdateResult {
  next: Candidate[];
  newResults: CandidateResult[];
  counts: ReturnType<typeof countByStatus>;
  progress: number;
  allDone: boolean;
  report: CampaignReport | null;
}

function applyLiveCandidatePollUpdate(
  prev: Candidate[],
  logs: Awaited<ReturnType<typeof fetchRecentCallLogs>>,
  options: {
    campaign: Campaign;
    candidateResults: CandidateResult[];
    dashboardStats: DashboardStats;
    reportGeneratedFor: string | null;
    callingSince: Map<string, number>;
    completedIds: Set<string>;
    candidateMeta: Map<string, ParsedCandidate>;
    resultIdRef: { current: number };
  },
): PollUpdateResult {
  const newResults: CandidateResult[] = [];

  const next = prev.map((candidate) => {
    if (candidate.dispatchFailed) return candidate;

    const log = findLatestCallLog(logs, candidate);

    let status = candidate.status;
    let duration = candidate.duration;

    if (log) {
      const mapped = mapOmnidimCallStatus(log.call_status);
      if (mapped) {
        status = mapped;
        if (mapped === 'calling' && !options.callingSince.has(candidate.id)) {
          options.callingSince.set(candidate.id, Date.now());
        }
        const logDuration = normalizeLogDuration(log.call_duration);
        if (logDuration) duration = logDuration;
      }
    }

    if (status === 'calling') {
      const started = options.callingSince.get(candidate.id) ?? Date.now();
      options.callingSince.set(candidate.id, started);
      duration = formatElapsedDuration(started);
    }

    if (status === 'completed' && !options.completedIds.has(candidate.id)) {
      options.completedIds.add(candidate.id);
      const parsed = options.candidateMeta.get(candidate.id);
      newResults.push(
        buildResultFromCandidate(
          { ...candidate, status, duration },
          parsed,
          String(options.resultIdRef.current++),
        ),
      );
    }

    return { ...candidate, status, duration };
  });

  const callLimit = getConcurrentCallLimit();
  let activeCalling = next.filter((c) => c.status === 'calling').length;
  for (const candidate of next) {
    if (candidate.dispatchFailed || candidate.status !== 'queued') continue;
    if (activeCalling >= callLimit) break;
    candidate.status = 'calling';
    candidate.duration = '00:00';
    options.callingSince.set(candidate.id, Date.now());
    activeCalling += 1;
  }

  const counts = countByStatus(next);
  const dialable = next.filter((c) => !c.dispatchFailed).length;
  const finished = counts.completed + counts.failed + counts.retry;
  const progress = dialable > 0 ? Math.round((finished / dialable) * 100) : 0;
  const allDone =
    counts.running === 0 && counts.queued === 0 && finished >= dialable;

  let report: CampaignReport | null = null;
  if (allDone && options.reportGeneratedFor !== options.campaign.id) {
    const allResults = [...options.candidateResults, ...newResults];
    const statsSnapshot: DashboardStats = {
      ...options.dashboardStats,
      totalCandidates: next.length,
      completedCalls: counts.completed,
      activeCalls: counts.running,
      pendingCalls: counts.queued,
      failedCalls: counts.dispatchFailed + counts.failed + counts.retry,
      qualifiedCandidates: counts.completed,
    };
    const completedCampaign: Campaign = {
      ...options.campaign,
      completed: counts.completed,
      running: counts.running,
      queued: counts.queued,
      progress: 100,
      status: 'completed',
    };
    report = buildCampaignReport(completedCampaign, next, allResults, statsSnapshot);
  }

  return { next, newResults, counts, progress, allDone, report };
}

function formatElapsedDuration(startedAt: number): string {
  const elapsed = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
  const m = Math.floor(elapsed / 60);
  const s = elapsed % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function normalizeLogDuration(raw?: string): string | null {
  if (!raw || raw === '0:0' || raw === '0:00') return null;
  const parts = raw.split(':');
  if (parts.length === 2) {
    return `${parts[0].padStart(2, '0')}:${parts[1].padStart(2, '0')}`;
  }
  return raw;
}

function buildLiveCandidateList(
  callable: ParsedCandidate[],
  dispatchById: Map<string, { success: boolean; requestId?: number }>,
  callingSince: Map<string, number>,
): Candidate[] {
  const limit = getConcurrentCallLimit();
  let callingSlots = limit;

  return callable.map((c) => {
    const dispatch = dispatchById.get(c.id);

    if (!dispatch?.success) {
      return {
        id: c.id,
        name: c.name,
        phone: c.phone,
        phoneNormalized: c.phoneNormalized ?? undefined,
        status: 'failed' as CallStatus,
        duration: '00:00',
        retry: 0,
        dispatchFailed: true,
      };
    }

    let status: CallStatus;
    if (callingSlots > 0) {
      status = 'calling';
      callingSlots -= 1;
      callingSince.set(c.id, Date.now());
    } else {
      status = 'queued';
    }

    return {
      id: c.id,
      name: c.name,
      phone: c.phone,
      phoneNormalized: c.phoneNormalized ?? undefined,
      status,
      duration: status === 'calling' ? '00:00' : '—',
      retry: 0,
      requestId: dispatch.requestId,
      dispatchFailed: false,
    };
  });
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [dashboardStats, setDashboardStats] = useState<DashboardStats>(emptyDashboardStats);
  const [campaign, setCampaign] = useState<Campaign>(idleCampaign);
  const [liveCandidates, setLiveCandidates] = useState<Candidate[]>([]);
  const [candidateResults, setCandidateResults] = useState<CandidateResult[]>([]);
  const [uploadedFile, setUploadedFileState] = useState<UploadedFile | null>(null);
  const [isCampaignRunning, setIsCampaignRunning] = useState(false);
  const [agentRunningSeconds, setAgentRunningSeconds] = useState(0);
  const [hasActiveCampaign, setHasActiveCampaign] = useState(false);
  const [campaignReports, setCampaignReports] = useState<CampaignReport[]>(() => loadStoredReports());

  const resultIdRef = useRef(0);
  const candidateMetaRef = useRef<Map<string, ParsedCandidate>>(new Map());
  const bulkCallIdRef = useRef<number | undefined>(undefined);
  const callingSinceRef = useRef<Map<string, number>>(new Map());
  const completedIdsRef = useRef<Set<string>>(new Set());
  const reportGeneratedRef = useRef<string | null>(null);
  const campaignRef = useRef(campaign);
  const candidateResultsRef = useRef(candidateResults);
  const dashboardStatsRef = useRef(dashboardStats);
  const liveCandidatesRef = useRef(liveCandidates);

  useEffect(() => {
    campaignRef.current = campaign;
  }, [campaign]);

  useEffect(() => {
    candidateResultsRef.current = candidateResults;
  }, [candidateResults]);

  useEffect(() => {
    dashboardStatsRef.current = dashboardStats;
  }, [dashboardStats]);

  useEffect(() => {
    liveCandidatesRef.current = liveCandidates;
  }, [liveCandidates]);

  useEffect(() => {
    const stored = loadStoredReports();
    if (stored.length > 0) {
      setCampaignReports(stored);
    }
  }, []);

  const saveReport = useCallback((report: CampaignReport) => {
    const stored = loadStoredReports();
    const filtered = stored.filter((r) => r.campaignId !== report.campaignId);
    const next = [report, ...filtered];
    saveStoredReports(next);
    setCampaignReports(next);
  }, []);

  const setUploadedFile = useCallback((file: UploadedFile | null) => {
    setUploadedFileState(file);
  }, []);

  const startCampaign = useCallback(
    async (
      name: string,
      onProgress?: DispatchProgressCallback,
    ): Promise<StartCampaignResult> => {
      const callable =
        uploadedFile?.candidates.filter((c) => c.phoneNormalized) ?? [];

      if (callable.length === 0) {
        return {
          success: false,
          dispatched: 0,
          failed: 0,
          error: 'No candidates with valid phone numbers to call.',
        };
      }

      const { results, dispatched, failed, bulkCallId } =
        await dispatchCampaignCalls(callable, name, onProgress);

      bulkCallIdRef.current = bulkCallId;
      completedIdsRef.current = new Set();
      callingSinceRef.current = new Map();
      reportGeneratedRef.current = null;

      if (dispatched === 0) {
        const errors = results.map((r) => r.error).filter(Boolean) as string[];
        return {
          success: false,
          dispatched: 0,
          failed,
          error: errors[0] ?? 'All call dispatches failed. Check OmniDimension API credentials.',
          errors,
        };
      }

      const dispatchById = new Map(results.map((r) => [r.candidateId, r]));
      candidateMetaRef.current = new Map(callable.map((c) => [c.id, c]));

      const total = callable.length;
      const dispatchFailedCount = results.filter((r) => !r.success).length;

      const now = new Date();
      const startedAt = now.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });

      const liveList = buildLiveCandidateList(callable, dispatchById, callingSinceRef.current);

      const counts = countByStatus(liveList);

      setCampaign({
        id: bulkCallId
          ? `CMP-BULK-${bulkCallId}`
          : `CMP-${now.getFullYear()}-${String(now.getTime()).slice(-4)}`,
        name,
        status: 'running',
        createdBy: 'HR Admin — Manav Raval',
        startedAt,
        totalCandidates: total,
        completed: counts.completed,
        running: counts.running,
        queued: counts.queued,
        retries: 0,
        averageDuration: '0m 00s',
        progress: 0,
      });

      setLiveCandidates(liveList);
      liveCandidatesRef.current = liveList;
      setCandidateResults([]);
      setIsCampaignRunning(true);
      setHasActiveCampaign(true);
      setAgentRunningSeconds(0);
      resultIdRef.current = 1;

      setDashboardStats({
        totalCandidates: total,
        completedCalls: counts.completed,
        activeCalls: counts.running,
        pendingCalls: counts.queued,
        failedCalls: dispatchFailedCount,
        qualifiedCandidates: 0,
      });

      return {
        success: true,
        dispatched,
        failed,
        errors: results.filter((r) => r.error).map((r) => `${r.candidateName}: ${r.error}`),
      };
    },
    [uploadedFile],
  );

  useEffect(() => {
    if (!isCampaignRunning || !hasActiveCampaign) return;

    const pollAndUpdate = async () => {
      setAgentRunningSeconds((s) => s + 5);

      const logs = await fetchRecentCallLogs(bulkCallIdRef.current);
      const update = applyLiveCandidatePollUpdate(
        liveCandidatesRef.current,
        logs,
        {
          campaign: campaignRef.current,
          candidateResults: candidateResultsRef.current,
          dashboardStats: dashboardStatsRef.current,
          reportGeneratedFor: reportGeneratedRef.current,
          callingSince: callingSinceRef.current,
          completedIds: completedIdsRef.current,
          candidateMeta: candidateMetaRef.current,
          resultIdRef,
        },
      );

      liveCandidatesRef.current = update.next;
      setLiveCandidates(update.next);

      setCampaign((c) => ({
        ...c,
        completed: update.counts.completed,
        running: update.counts.running,
        queued: update.counts.queued,
        progress: update.progress,
        status: update.allDone ? 'completed' : 'running',
      }));

      setDashboardStats({
        totalCandidates: update.next.length,
        completedCalls: update.counts.completed,
        activeCalls: update.counts.running,
        pendingCalls: update.counts.queued,
        failedCalls:
          update.counts.dispatchFailed + update.counts.failed + update.counts.retry,
        qualifiedCandidates: update.counts.completed,
      });

      if (update.newResults.length > 0) {
        setCandidateResults((prev) => {
          const merged = [...prev, ...update.newResults];
          candidateResultsRef.current = merged;
          return merged;
        });
      }

      if (update.allDone) {
        setIsCampaignRunning(false);
        if (update.report && reportGeneratedRef.current !== campaignRef.current.id) {
          reportGeneratedRef.current = campaignRef.current.id;
          saveReport(update.report);
        }
      }
    };

    pollAndUpdate();
    const interval = setInterval(pollAndUpdate, 5000);
    return () => clearInterval(interval);
  }, [isCampaignRunning, hasActiveCampaign, saveReport]);

  const value = useMemo(
    () => ({
      dashboardStats,
      campaign,
      liveCandidates,
      candidateResults,
      campaignReports,
      uploadedFile,
      isCampaignRunning,
      agentRunningSeconds,
      hasActiveCampaign,
      setUploadedFile,
      startCampaign,
    }),
    [
      dashboardStats,
      campaign,
      liveCandidates,
      candidateResults,
      campaignReports,
      uploadedFile,
      isCampaignRunning,
      agentRunningSeconds,
      hasActiveCampaign,
      setUploadedFile,
      startCampaign,
    ],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}
