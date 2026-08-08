import { useQuery } from '@tanstack/react-query';
import { Ship, Truck, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { shipmentsApi } from '@/api';
import { formatDate, shipmentStatusColor } from '@/utils/format';
import type { Shipment } from '@/types';

export function ShipmentsPage() {
  const { data: shipData, isLoading } = useQuery({
    queryKey: ['shipments'],
    queryFn: () => shipmentsApi.list({ page_size: 50 }),
  });

  const shipments = shipData?.data?.items ?? [];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Shipments & In-Transit Tracking</h1>
        <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
          Inbound vendor shipments and outbound customer order logistics
        </p>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading shipments...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Tracking #</th>
                <th>Type</th>
                <th>Carrier</th>
                <th>Origin</th>
                <th>Destination</th>
                <th>Status</th>
                <th>Expected Date</th>
              </tr>
            </thead>
            <tbody>
              {shipments.map((s: Shipment) => {
                const statusBadge = `badge-${shipmentStatusColor(s.status)}`;
                return (
                  <tr key={s.id}>
                    <td><code style={{ color: 'hsl(var(--color-primary))', fontWeight: 600 }}>{s.tracking_number || s.id.slice(0, 8)}</code></td>
                    <td><span className="badge badge-neutral">{s.shipment_type}</span></td>
                    <td style={{ fontWeight: 600 }}>{s.carrier || 'Unassigned'}</td>
                    <td>{s.origin || '—'}</td>
                    <td>{s.destination || '—'}</td>
                    <td><span className={`badge ${statusBadge}`}>{s.status.replace('_', ' ')}</span></td>
                    <td>{formatDate(s.expected_date)}</td>
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
