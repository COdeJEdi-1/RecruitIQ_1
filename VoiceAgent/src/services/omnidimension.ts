import type { ParsedCandidate } from '../types';

const API_BASE = '/api/omnidim';
const CALL_DELAY_MS = 5000;
const DISPATCH_RETRY_ATTEMPTS = 3;
const DISPATCH_RETRY_DELAY_MS = 4000;
const DEFAULT_CONCURRENT_CALLS = 4;

export function getConcurrentCallLimit(): number {
  const raw = import.meta.env.VITE_OMNIDIM_CONCURRENT_CALLS;
  const parsed = raw ? Number(raw) : DEFAULT_CONCURRENT_CALLS;
  if (!Number.isFinite(parsed) || parsed < 1) return DEFAULT_CONCURRENT_CALLS;
  return Math.min(Math.floor(parsed), 10);
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getConfig() {
  const agentId = import.meta.env.VITE_OMNIDIM_AGENT_ID;
  const apiKey = import.meta.env.VITE_OMNIDIM_API_KEY;

  if (!agentId || !apiKey) {
    throw new Error(
      'OmniDimension credentials missing. Set VITE_OMNIDIM_AGENT_ID and VITE_OMNIDIM_API_KEY in .env',
    );
  }

  return {
    agentId: Number(agentId),
    apiKey,
  };
}

function authHeaders(apiKey: string) {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${apiKey}`,
  };
}

function sanitizeKey(key: string): string {
  return key
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '')
    .slice(0, 48);
}

export function phonesMatch(a: string, b: string): boolean {
  const da = a.replace(/\D/g, '');
  const db = b.replace(/\D/g, '');
  if (!da || !db) return false;
  if (da === db) return true;
  if (da.length >= 10 && db.length >= 10) {
    return da.slice(-10) === db.slice(-10);
  }
  return false;
}

function buildContactRow(candidate: ParsedCandidate, campaignName: string) {
  const row: Record<string, string> = {
    phone_number: candidate.phoneNormalized!,
    candidate_name: candidate.name,
    campaign_name: campaignName,
  };

  if (candidate.email) row.candidate_email = candidate.email;

  Object.entries(candidate.raw).forEach(([key, value]) => {
    if (!value) return;
    const safeKey = sanitizeKey(key);
    if (safeKey && !row[safeKey]) {
      row[safeKey] = String(value).slice(0, 300);
    }
  });

  return row;
}

function buildCallContext(candidate: ParsedCandidate, campaignName: string): Record<string, string> {
  const row = buildContactRow(candidate, campaignName);
  const { phone_number: _p, ...context } = row;
  return context;
}

function extractApiError(data: unknown, status: number): string {
  if (!data || typeof data !== 'object') return `API error ${status}`;

  const obj = data as Record<string, unknown>;

  if (typeof obj.message === 'string') return obj.message;
  if (typeof obj.error === 'string') return obj.error;
  if (typeof obj.detail === 'string') return obj.detail;

  if (Array.isArray(obj.detail)) {
    return obj.detail.map((d) => String(d)).join(', ');
  }

  if (obj.errors && typeof obj.errors === 'object') {
    return JSON.stringify(obj.errors);
  }

  return `API error ${status}`;
}

export interface DispatchCallResult {
  success: boolean;
  candidateId: string;
  candidateName: string;
  phone: string;
  requestId?: number;
  error?: string;
}

export interface BulkCampaignResult {
  success: boolean;
  bulkCallId?: number;
  error?: string;
}

export interface OmnidimCallLog {
  id: number;
  to_number?: string;
  call_status?: string;
  call_duration?: string;
  call_request_id?: number;
}

async function getPhoneNumberId(apiKey: string): Promise<string> {
  const fromEnv = import.meta.env.VITE_OMNIDIM_PHONE_NUMBER_ID;
  if (fromEnv) return String(fromEnv);

  const response = await fetch(`${API_BASE}/phone_number/list`, {
    headers: authHeaders(apiKey),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(extractApiError(data, response.status));
  }

  const list =
    (data as { phone_numbers?: { id: number | string }[] }).phone_numbers ??
    (data as { data?: { id: number | string }[] }).data ??
    [];

  const first = list[0]?.id;
  if (!first) {
    throw new Error(
      'No outbound phone number found in OmniDimension. Set VITE_OMNIDIM_PHONE_NUMBER_ID in .env',
    );
  }

  return String(first);
}

export async function createBulkCampaign(
  campaignName: string,
  candidates: ParsedCandidate[],
): Promise<BulkCampaignResult> {
  const { apiKey } = getConfig();

  try {
    const phoneNumberId = await getPhoneNumberId(apiKey);
    const contactList = candidates
      .filter((c) => c.phoneNormalized)
      .map((c) => buildContactRow(c, campaignName));

    const response = await fetch(`${API_BASE}/calls/bulk_call/create`, {
      method: 'POST',
      headers: authHeaders(apiKey),
      body: JSON.stringify({
        name: campaignName,
        phone_number_id: phoneNumberId,
        contact_list: contactList,
        concurrent_call_limit: getConcurrentCallLimit(),
        enabled_reschedule_call: true,
        retry_config: {
          auto_retry: true,
          auto_retry_schedule: 'immediately',
          retry_limit: 2,
        },
      }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      return { success: false, error: extractApiError(data, response.status) };
    }

    const bulkCallId = (data as { id?: number }).id;
    if (!bulkCallId) {
      return { success: false, error: 'Bulk campaign created but no campaign ID returned.' };
    }

    return { success: true, bulkCallId };
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Failed to create bulk campaign',
    };
  }
}

export async function dispatchOmnidimCall(
  toNumber: string,
  callContext: Record<string, string>,
): Promise<{ success: boolean; requestId?: number; error?: string }> {
  const { agentId, apiKey } = getConfig();

  const response = await fetch(`${API_BASE}/calls/dispatch`, {
    method: 'POST',
    headers: authHeaders(apiKey),
    body: JSON.stringify({
      agent_id: agentId,
      to_number: toNumber,
      call_context: callContext,
    }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    return { success: false, error: extractApiError(data, response.status) };
  }

  const success =
    data.success !== false &&
    (data.status === 'dispatched' || data.success === true || Boolean(data.requestId));

  return {
    success,
    requestId: data.requestId,
    error: success ? undefined : extractApiError(data, response.status),
  };
}

async function dispatchWithRetry(
  candidate: ParsedCandidate,
  campaignName: string,
): Promise<DispatchCallResult> {
  let lastError = 'Unknown error';

  for (let attempt = 0; attempt < DISPATCH_RETRY_ATTEMPTS; attempt++) {
    if (attempt > 0) {
      await sleep(DISPATCH_RETRY_DELAY_MS);
    }

    try {
      const callContext = buildCallContext(candidate, campaignName);
      const result = await dispatchOmnidimCall(candidate.phoneNormalized!, callContext);

      if (result.success) {
        return {
          success: true,
          candidateId: candidate.id,
          candidateName: candidate.name,
          phone: candidate.phoneNormalized!,
          requestId: result.requestId,
        };
      }

      lastError = result.error ?? lastError;
    } catch (err) {
      lastError = err instanceof Error ? err.message : 'Network error';
    }
  }

  return {
    success: false,
    candidateId: candidate.id,
    candidateName: candidate.name,
    phone: candidate.phoneNormalized!,
    error: lastError,
  };
}

export type DispatchProgressCallback = (
  current: number,
  total: number,
  candidateName: string,
  message?: string,
) => void;

export async function dispatchCampaignCalls(
  candidates: ParsedCandidate[],
  campaignName: string,
  onProgress?: DispatchProgressCallback,
): Promise<{
  results: DispatchCallResult[];
  dispatched: number;
  failed: number;
  bulkCallId?: number;
  usedBulkCall: boolean;
}> {
  const callable = candidates.filter((c) => c.phoneNormalized);

  onProgress?.(0, callable.length, '', 'Creating bulk call campaign...');
  const bulk = await createBulkCampaign(campaignName, callable);

  if (bulk.success && bulk.bulkCallId) {
    const results: DispatchCallResult[] = callable.map((c) => ({
      success: true,
      candidateId: c.id,
      candidateName: c.name,
      phone: c.phoneNormalized!,
    }));

    return {
      results,
      dispatched: callable.length,
      failed: 0,
      bulkCallId: bulk.bulkCallId,
      usedBulkCall: true,
    };
  }

  onProgress?.(0, callable.length, '', `Bulk call unavailable (${bulk.error}). Dispatching in batches of ${getConcurrentCallLimit()}...`);

  const results: DispatchCallResult[] = [];
  const batchSize = getConcurrentCallLimit();

  for (let i = 0; i < callable.length; i += batchSize) {
    const batch = callable.slice(i, i + batchSize);

    if (i > 0) {
      await sleep(CALL_DELAY_MS);
    }

    onProgress?.(
      Math.min(i + batchSize, callable.length),
      callable.length,
      '',
      `Dispatching batch ${Math.floor(i / batchSize) + 1} (${batch.length} calls in parallel)`,
    );

    const batchResults = await Promise.all(
      batch.map((candidate) => dispatchWithRetry(candidate, campaignName)),
    );
    results.push(...batchResults);
  }

  const dispatched = results.filter((r) => r.success).length;

  return {
    results,
    dispatched,
    failed: results.length - dispatched,
    usedBulkCall: false,
  };
}

export async function fetchRecentCallLogs(
  bulkCallId?: number,
): Promise<OmnidimCallLog[]> {
  const { agentId, apiKey } = getConfig();

  const params = new URLSearchParams({
    agentid: String(agentId),
    pagesize: '100',
    pageno: '1',
  });

  if (bulkCallId) {
    params.set('bulk_call_id', String(bulkCallId));
  }

  const response = await fetch(`${API_BASE}/calls/logs?${params.toString()}`, {
    headers: authHeaders(apiKey),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    return [];
  }

  return ((data as { call_log_data?: OmnidimCallLog[] }).call_log_data ?? []) as OmnidimCallLog[];
}

export function findLatestCallLog(
  logs: OmnidimCallLog[],
  candidate: { phoneNormalized?: string; requestId?: number },
): OmnidimCallLog | undefined {
  const matching = logs.filter(
    (l) =>
      (l.to_number &&
        candidate.phoneNormalized &&
        phonesMatch(l.to_number, candidate.phoneNormalized)) ||
      (l.call_request_id && l.call_request_id === candidate.requestId),
  );

  if (matching.length === 0) return undefined;

  return matching.reduce((latest, log) => (log.id > latest.id ? log : latest));
}

export function mapOmnidimCallStatus(apiStatus?: string): import('../types').CallStatus | null {
  if (!apiStatus) return null;

  const s = apiStatus.toLowerCase().replace(/[_\s-]+/g, '');

  if (s === 'completed' || s === 'answered') return 'completed';
  if (s === 'failed') return 'failed';
  if (s === 'busy') return 'retry';
  if (s === 'noanswer') return 'retry';
  if (s === 'inprogress' || s === 'ringing' || s === 'dispatched' || s === 'ongoing') {
    return 'calling';
  }
  if (s === 'queued' || s === 'pending') return 'queued';

  return null;
}
