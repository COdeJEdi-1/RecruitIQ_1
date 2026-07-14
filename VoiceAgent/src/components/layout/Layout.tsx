import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { ArrowLeft } from 'lucide-react';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/new-campaign': 'New Campaign',
  '/campaign-monitoring': 'Campaign Monitoring',
  '/reports': 'Reports',
  '/analytics': 'Analytics',
  '/settings': 'Settings',
  '/help': 'Help & Support',
};

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const title = pageTitles[location.pathname] ?? 'Dashboard';

  return (
    <div className="min-h-screen bg-surface-bg">
      {/* Back button — fixed top left */}
      <button
        onClick={() => navigate(-1)}
        title="Go back"
        className="fixed top-4 left-4 z-50 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/90 backdrop-blur-sm border border-grey-border text-xs font-semibold text-grey-secondary hover:text-maroon hover:border-maroon transition-all shadow-sm"
      >
        <ArrowLeft className="h-3.5 w-3.5" strokeWidth={2} />
        Back
      </button>

      <Sidebar />
      <div className="ml-sidebar">
        <Header title={title} />
        <main className="layout-container py-8 animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
