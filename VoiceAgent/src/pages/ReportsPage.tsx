import { FileText, Download, Calendar, Filter } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { useApp } from '../context/AppContext';
import { downloadCampaignReport } from '../utils/generateReport';

export function ReportsPage() {
  const { campaignReports } = useApp();

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-heading text-gray-900">Campaign Reports</h2>
          <p className="mt-1 text-sm text-grey-secondary">
            Reports are generated automatically when a campaign completes and saved here for download.
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary">
            <Filter className="h-4 w-4" strokeWidth={1.75} />
            Filter
          </Button>
          <Button variant="secondary">
            <Calendar className="h-4 w-4" strokeWidth={1.75} />
            Date Range
          </Button>
        </div>
      </div>

      {campaignReports.length === 0 ? (
        <Card className="animate-slide-up py-16 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-maroon/10">
            <FileText className="h-7 w-7 text-maroon" strokeWidth={1.75} />
          </div>
          <h3 className="font-heading text-gray-900">No Reports Yet</h3>
          <p className="mx-auto mt-2 max-w-md text-sm text-grey-secondary">
            Complete a campaign to automatically generate and save a downloadable report here.
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {campaignReports.map((report, i) => (
            <Card
              key={report.id}
              hover
              className="animate-slide-up"
              {...({ style: { animationDelay: `${i * 60}ms`, animationFillMode: 'both' } } as object)}
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-maroon/8">
                    <FileText className="h-6 w-6 text-maroon" strokeWidth={1.75} />
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-heading text-gray-900">{report.name}</h3>
                      <Badge variant={report.status === 'ready' ? 'success' : 'info'}>
                        {report.status === 'ready' ? 'Ready' : 'Processing'}
                      </Badge>
                    </div>
                    <p className="mt-1 text-sm text-grey-secondary">
                      {report.campaignId} · {report.candidates} candidates · {report.date}
                    </p>
                    <p className="mt-1 text-xs text-grey-secondary">
                      Completed: {report.summary.completedCalls} · Failed: {report.summary.failedCalls} ·
                      Qualified: {report.summary.qualifiedCandidates}
                    </p>
                  </div>
                </div>
                <Button
                  variant={report.status === 'ready' ? 'primary' : 'secondary'}
                  disabled={report.status !== 'ready'}
                  className="shrink-0"
                  onClick={() => downloadCampaignReport(report)}
                >
                  <Download className="h-4 w-4" strokeWidth={1.75} />
                  Download Report
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
