import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ClipboardList, CheckCircle, Package, Truck } from 'lucide-react';
import { salesOrdersApi, customersApi, warehousesApi } from '@/api';
import { soStatusColor, formatDate } from '@/utils/format';
import type { SalesOrder } from '@/types';

export function SalesOrdersPage() {
  const queryClient = useQueryClient();

  const { data: soData, isLoading } = useQuery({
    queryKey: ['sales-orders'],
    queryFn: () => salesOrdersApi.list({ page_size: 50 }),
  });

  const { data: custData } = useQuery({ queryKey: ['customers'], queryFn: () => customersApi.list({ page_size: 100 }) });
  const { data: whData } = useQuery({ queryKey: ['warehouses'], queryFn: () => warehousesApi.list({ page_size: 50 }) });

  const sos = soData?.data?.items ?? [];
  const customers = custData?.data?.items ?? [];
  const warehouses = whData?.data?.items ?? [];

  const confirmMutation = useMutation({
    mutationFn: (id: string) => salesOrdersApi.confirm(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sales-orders'] }),
  });

  const fulfillMutation = useMutation({
    mutationFn: (id: string) => salesOrdersApi.fulfill(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sales-orders'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });

  const shipMutation = useMutation({
    mutationFn: (id: string) => salesOrdersApi.ship(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['sales-orders'] }),
  });

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Sales Orders</h1>
        <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
          Fulfillment lifecycle: Draft → Confirmed → Fulfilled → Shipped → Delivered
        </p>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading sales orders...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>SO ID</th>
                <th>Customer</th>
                <th>Fulfillment Warehouse</th>
                <th>Order Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sos.map((so: SalesOrder) => {
                const cust = customers.find(c => c.id === so.customer_id);
                const wh = warehouses.find(w => w.id === so.warehouse_id);
                const statusBadge = `badge-${soStatusColor(so.status)}`;

                return (
                  <tr key={so.id}>
                    <td><code style={{ color: 'hsl(var(--color-primary))', fontWeight: 600 }}>SO-{so.id.slice(0, 8)}</code></td>
                    <td style={{ fontWeight: 600, color: 'hsl(var(--color-text-primary))' }}>{cust?.name || '—'}</td>
                    <td>{wh?.name || '—'}</td>
                    <td>{new Date(so.created_at).toLocaleDateString()}</td>
                    <td><span className={`badge ${statusBadge}`}>{so.status}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {so.status === 'draft' && (
                          <button className="btn btn-secondary btn-sm" onClick={() => confirmMutation.mutate(so.id)}>
                            <CheckCircle size={13} /> Confirm
                          </button>
                        )}
                        {so.status === 'confirmed' && (
                          <button className="btn btn-primary btn-sm" onClick={() => fulfillMutation.mutate(so.id)}>
                            <Package size={13} /> Fulfill Stock
                          </button>
                        )}
                        {so.status === 'fulfilled' && (
                          <button className="btn btn-primary btn-sm" onClick={() => shipMutation.mutate(so.id)}>
                            <Truck size={13} /> Mark Shipped
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
