import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AlertTriangle, CheckCircle, Eye } from 'lucide-react';
import { alertsApi } from '@/api';
import { formatRelative } from '@/utils/format';
import type { Alert } from '@/types';

export function AlertsPage() {
  const queryClient = useQueryClient();
  const [filterSeverity, setFilterSeverity] = useState<string>('');

  const { data: alertData, isLoading } = useQuery({
    queryKey: ['alerts', filterSeverity],
    queryFn: () => alertsApi.list({ page_size: 50, severity: filterSeverity || undefined }),
  });

  const alerts = alertData?.data?.items ?? [];

  const updateMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => alertsApi.update(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  });

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>System Alerts</h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Low stock, warehouse capacity, and supplier delay warnings
          </p>
        </div>
        <select className="form-input" style={{ width: 160 }} value={filterSeverity} onChange={e => setFilterSeverity(e.target.value)}>
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading alerts...</div>
        ) : alerts.length === 0 ? (
          <div className="empty-state" style={{ padding: '4rem' }}>
            <CheckCircle size={40} style={{ color: 'hsl(var(--color-success))' }} />
            <p>No open alerts found</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Type</th>
                <th>Alert Message</th>
                <th>Created</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a: Alert) => {
                const sevBadge = a.severity === 'critical' ? 'badge-danger' : a.severity === 'warning' ? 'badge-warning' : 'badge-info';
                return (
                  <tr key={a.id}>
                    <td><span className={`badge ${sevBadge}`}>{a.severity}</span></td>
                    <td><code style={{ fontSize: '0.75rem' }}>{a.alert_type}</code></td>
                    <td style={{ maxWidth: 480, lineHeight: 1.5, color: 'hsl(var(--color-text-primary))' }}>{a.message}</td>
                    <td style={{ fontSize: '0.8rem', color: 'hsl(var(--color-text-muted))' }}>{formatRelative(a.created_at)}</td>
                    <td><span className="badge badge-neutral">{a.status}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {a.status === 'open' && (
                          <button className="btn btn-secondary btn-sm" onClick={() => updateMutation.mutate({ id: a.id, status: 'acknowledged' })}>
                            Acknowledge
                          </button>
                        )}
                        {a.status !== 'resolved' && (
                          <button className="btn btn-primary btn-sm" onClick={() => updateMutation.mutate({ id: a.id, status: 'resolved' })}>
                            Resolve
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
