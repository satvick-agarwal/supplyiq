import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ShoppingCart, Plus, CheckCircle, Send, PackageCheck, XCircle, Clock } from 'lucide-react';
import { purchaseOrdersApi, suppliersApi, warehousesApi, productsApi } from '@/api';
import { formatDate, poStatusColor } from '@/utils/format';
import type { PurchaseOrder, Supplier, Warehouse, Product } from '@/types';

export function PurchaseOrdersPage() {
  const queryClient = useQueryClient();
  const [selectedPo, setSelectedPo] = useState<PurchaseOrder | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showReceiveModal, setShowReceiveModal] = useState(false);
  const [receiveQty, setReceiveQty] = useState<Record<string, number>>({});

  const { data: poData, isLoading } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: () => purchaseOrdersApi.list({ page_size: 50 }),
  });

  const { data: supData } = useQuery({ queryKey: ['suppliers'], queryFn: () => suppliersApi.list({ page_size: 100 }) });
  const { data: whData } = useQuery({ queryKey: ['warehouses'], queryFn: () => warehousesApi.list({ page_size: 50 }) });
  const { data: prodData } = useQuery({ queryKey: ['products'], queryFn: () => productsApi.list({ page_size: 100 }) });

  const pos = poData?.data?.items ?? [];
  const suppliers = supData?.data?.items ?? [];
  const warehouses = whData?.data?.items ?? [];
  const products = prodData?.data?.items ?? [];

  // Action mutations
  const approveMutation = useMutation({
    mutationFn: (id: string) => purchaseOrdersApi.approve(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['purchase-orders'] }),
  });

  const sendMutation = useMutation({
    mutationFn: (id: string) => purchaseOrdersApi.send(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['purchase-orders'] }),
  });

  const receiveMutation = useMutation({
    mutationFn: ({ id, items }: { id: string; items: Array<{ product_id: string; quantity_received: number }> }) =>
      purchaseOrdersApi.receive(id, items),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['purchase-orders'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      setShowReceiveModal(false);
    },
  });

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Purchase Orders</h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Procurement lifecycle: Draft → Approve → Send → Receive → Close
          </p>
        </div>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading purchase orders...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>PO ID</th>
                <th>Supplier</th>
                <th>Destination Warehouse</th>
                <th>Order Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pos.map((po: PurchaseOrder) => {
                const sup = suppliers.find(s => s.id === po.supplier_id);
                const wh = warehouses.find(w => w.id === po.warehouse_id);
                const statusBadge = `badge-${poStatusColor(po.status)}`;

                return (
                  <tr key={po.id}>
                    <td><code style={{ color: 'hsl(var(--color-primary))', fontWeight: 600 }}>PO-{po.id.slice(0, 8)}</code></td>
                    <td style={{ fontWeight: 600, color: 'hsl(var(--color-text-primary))' }}>{sup?.name || '—'}</td>
                    <td>{wh?.name || '—'}</td>
                    <td>{formatDate(po.order_date)}</td>
                    <td><span className={`badge ${statusBadge}`}>{po.status.replace('_', ' ')}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {po.status === 'draft' && (
                          <button className="btn btn-secondary btn-sm" onClick={() => approveMutation.mutate(po.id)}>
                            <CheckCircle size={13} /> Approve
                          </button>
                        )}
                        {po.status === 'approved' && (
                          <button className="btn btn-primary btn-sm" onClick={() => sendMutation.mutate(po.id)}>
                            <Send size={13} /> Send to Vendor
                          </button>
                        )}
                        {(po.status === 'sent' || po.status === 'partially_received') && (
                          <button className="btn btn-primary btn-sm" onClick={() => { setSelectedPo(po); setShowReceiveModal(true); }}>
                            <PackageCheck size={13} /> Receive Goods
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

      {/* Receive Goods Modal */}
      {showReceiveModal && selectedPo && (
        <div className="modal-overlay" onClick={() => setShowReceiveModal(false)}>
          <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', marginBottom: '0.5rem' }}>
              Receive Goods for PO-{selectedPo.id.slice(0, 8)}
            </h2>
            <p style={{ fontSize: '0.8rem', color: 'hsl(var(--color-text-muted))', marginBottom: '1.25rem' }}>
              Receiving inventory will atomically increment stock on hand in the warehouse.
            </p>
            <form onSubmit={e => {
              e.preventDefault();
              const items = selectedPo.items.map(item => ({
                product_id: item.product_id,
                quantity_received: receiveQty[item.product_id] || (parseFloat(item.quantity_ordered) - parseFloat(item.quantity_received)),
              }));
              receiveMutation.mutate({ id: selectedPo.id, items });
            }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Ordered</th>
                    <th>Previously Received</th>
                    <th>Receive Now</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedPo.items.map(item => {
                    const prod = products.find(p => p.id === item.product_id);
                    const remaining = parseFloat(item.quantity_ordered) - parseFloat(item.quantity_received);
                    return (
                      <tr key={item.id}>
                        <td>{prod?.name || item.product_id.slice(0, 8)}</td>
                        <td>{parseFloat(item.quantity_ordered).toLocaleString()}</td>
                        <td>{parseFloat(item.quantity_received).toLocaleString()}</td>
                        <td>
                          <input
                            className="form-input"
                            type="number"
                            style={{ width: 120 }}
                            defaultValue={remaining}
                            max={remaining}
                            min="0"
                            onChange={e => setReceiveQty({ ...receiveQty, [item.product_id]: parseFloat(e.target.value) || 0 })}
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowReceiveModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={receiveMutation.isPending}>Confirm Receipt</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
