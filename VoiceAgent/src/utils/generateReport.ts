import type { Campaign, CampaignReport, Candidate, CandidateResult, DashboardStats } from '../types';

const REPORTS_STORAGE_KEY = 'arvind_gcc_campaign_reports';

function escapeCsv(value: string | number): string {
  const str = String(value ?? '');
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function sanitizeFilename(name: string): string {
  return name.replace(/[^a-z0-9-_]+/gi, '-').replace(/-+/g, '-').slice(0, 80);
}

export function buildCampaignReport(
  campaign: Campaign,
  liveCandidates: Candidate[],
  results: CandidateResult[],
  stats: DashboardStats,
): CampaignReport {
  const completedAt = new Date();

  return {
    id: `RPT-${campaign.id}-${completedAt.getTime()}`,
    name: `${campaign.name} — Report`,
    campaignId: campaign.id,
    campaignName: campaign.name,
    date: completedAt.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }),
    completedAt: completedAt.toISOString(),
    candidates: campaign.totalCandidates,
    status: 'ready',
    summary: {
      totalCandidates: stats.totalCandidates,
      completedCalls: stats.completedCalls,
      failedCalls: stats.failedCalls,
      activeCalls: stats.activeCalls,
      pendingCalls: stats.pendingCalls,
      qualifiedCandidates: stats.qualifiedCandidates,
      campaignProgress: campaign.progress,
      createdBy: campaign.createdBy,
      startedAt: campaign.startedAt,
    },
    candidateRows: liveCandidates.map((c) => ({
      name: c.name,
      phone: c.phone,
      status: c.status,
    })),
    results,
  };
}

export function reportToCsv(report: CampaignReport): string {
  const lines: string[] = [];

  lines.push('Arvind GCC — Campaign Report');
  lines.push('');
  lines.push(`Campaign Name,${escapeCsv(report.campaignName)}`);
  lines.push(`Campaign ID,${escapeCsv(report.campaignId)}`);
  lines.push(`Report Generated,${escapeCsv(report.date)}`);
  lines.push(`Started At,${escapeCsv(report.summary.startedAt)}`);
  lines.push(`Created By,${escapeCsv(report.summary.createdBy)}`);
  lines.push('');
  lines.push('Summary');
  lines.push(`Total Candidates,${report.summary.totalCandidates}`);
  lines.push(`Completed Calls,${report.summary.completedCalls}`);
  lines.push(`Failed Calls,${report.summary.failedCalls}`);
  lines.push(`Qualified Candidates,${report.summary.qualifiedCandidates}`);
  lines.push(`Campaign Progress,${report.summary.campaignProgress}%`);
  lines.push('');
  lines.push('Live Candidate Status');
  lines.push('Name,Phone,Status');
  report.candidateRows.forEach((row) => {
    lines.push(
      [escapeCsv(row.name), escapeCsv(row.phone), escapeCsv(row.status)].join(','),
    );
  });
  lines.push('');
  lines.push('Candidate Results');
  lines.push(
    'Name,Experience,Current CTC,Expected CTC,Notice Period,Current Location,Preferred Location,Shift,Job Change,Result,Status',
  );
  report.results.forEach((row) => {
    lines.push(
      [
        escapeCsv(row.name),
        escapeCsv(row.experience),
        escapeCsv(row.currentCtc),
        escapeCsv(row.expectedCtc),
        escapeCsv(row.noticePeriod),
        escapeCsv(row.currentLocation),
        escapeCsv(row.preferredLocation),
        escapeCsv(row.shift),
        escapeCsv(row.jobChange),
        escapeCsv(row.result),
        escapeCsv(row.status),
      ].join(','),
    );
  });

  return lines.join('\n');
}

export function downloadCampaignReport(report: CampaignReport): void {
  const csv = reportToCsv(report);
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${sanitizeFilename(report.campaignName)}-report.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function loadStoredReports(): CampaignReport[] {
  try {
    const raw = localStorage.getItem(REPORTS_STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as CampaignReport[];
  } catch {
    return [];
  }
}

export function saveStoredReports(reports: CampaignReport[]): void {
  try {
    localStorage.setItem(REPORTS_STORAGE_KEY, JSON.stringify(reports));
  } catch (err) {
    console.error('Failed to save campaign reports to localStorage:', err);
  }
}
