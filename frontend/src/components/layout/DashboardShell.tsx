import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { cn } from '@/utils/cn';

export function DashboardShell() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      <div className={cn('page-content', collapsed && 'collapsed')} style={{ flex: 1 }}>
        <Topbar />
        <main className="page-inner">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
