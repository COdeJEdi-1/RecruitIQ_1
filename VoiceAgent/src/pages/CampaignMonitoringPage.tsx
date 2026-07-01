import { CampaignHeader, CampaignKPIs, CampaignProgress } from '../components/campaign/CampaignOverview';
import { LiveCandidateTable } from '../components/campaign/CandidateTables';
import { AIAgentCard } from '../components/AIAgentCard';
import { useApp } from '../context/AppContext';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useNavigate } from 'react-router-dom';
import { Phone } from 'lucide-react';

export function CampaignMonitoringPage() {
  const { hasActiveCampaign } = useApp();
  const navigate = useNavigate();

  if (!hasActiveCampaign) {
    return (
      <Card className="animate-slide-up py-16 text-center">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-maroon/10">
          <Phone className="h-8 w-8 text-maroon" strokeWidth={1.75} />
        </div>
        <h2 className="text-xl font-heading text-gray-900">No Active Campaign</h2>
        <p className="mx-auto mt-2 max-w-md text-sm text-grey-secondary">
          Start a new campaign from New Campaign to dispatch AI screening calls and monitor live
          progress here.
        </p>
        <Button className="mt-6" onClick={() => navigate('/new-campaign')}>
          Create New Campaign
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-8 pb-32">
      <CampaignHeader />
      <CampaignKPIs />
      <CampaignProgress />
      <LiveCandidateTable />
      <AIAgentCard />
    </div>
  );
}
