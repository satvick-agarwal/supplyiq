import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Package, ArrowRightLeft, Sliders, AlertTriangle, Layers } from 'lucide-react';
import { inventoryApi, productsApi, warehousesApi } from '@/api';
import type { InventoryItem, InventoryMovement, Product, Warehouse } from '@/types';

export function InventoryPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<'on_hand' | 'movements'>('on_hand');
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);

  // Adjust form
  const [adjustForm, setAdjustForm] = useState({ product_id: '', warehouse_id: '', quantity: 0, reason: '' });
  // Transfer form
  const [transferForm, setTransferForm] = useState({ product_id: '', from_warehouse_id: '', to_warehouse_id: '', quantity: 0, reason: '' });

  const { data: invData, isLoading: invLoading } = useQuery({
    queryKey: ['inventory', lowStockOnly],
    queryFn: () => lowStockOnly ? inventoryApi.lowStock({ page_size: 50 }) : inventoryApi.list({ page_size: 50 }),
  });

  const { data: moveData, isLoading: moveLoading } = useQuery({
    queryKey: ['inventory-movements'],
    queryFn: () => inventoryApi.movements({ page_size: 50 }),
    enabled: tab === 'movements',
  });

  const { data: prodData } = useQuery({ queryKey: ['products'], queryFn: () => productsApi.list({ page_size: 100 }) });
  const { data: whData } = useQuery({ queryKey: ['warehouses'], queryFn: () => warehousesApi.list({ page_size: 50 }) });

  const inventory = invData?.data?.items ?? [];
  const movements = moveData?.data?.items ?? [];
  const products = prodData?.data?.items ?? [];
  const warehouses = whData?.data?.items ?? [];

  const adjustMutation = useMutation({
    mutationFn: inventoryApi.adjust,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-movements'] });
      setShowAdjustModal(false);
    },
  });

  const transferMutation = useMutation({
    mutationFn: inventoryApi.transfer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['inventory-movements'] });
      setShowTransferModal(false);
    },
  });

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Inventory & Stock Ledger</h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Append-only movement ledger, stock adjustments, and warehouse transfers
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={() => setShowTransferModal(true)}>
            <ArrowRightLeft size={16} /> Transfer Stock
          </button>
          <button className="btn btn-primary" onClick={() => setShowAdjustModal(true)}>
            <Sliders size={16} /> Adjust Stock
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid hsl(var(--color-border))', gap: '1rem' }}>
        <button
          onClick={() => setTab('on_hand')}
          style={{
            padding: '0.75rem 1rem', border: 'none', background: 'none',
            fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer',
            color: tab === 'on_hand' ? 'hsl(var(--color-primary))' : 'hsl(var(--color-text-muted))',
            borderBottom: tab === 'on_hand' ? '2px solid hsl(var(--color-primary))' : 'none',
          }}
        >
          Stock On Hand
        </button>
        <button
          onClick={() => setTab('movements')}
          style={{
            padding: '0.75rem 1rem', border: 'none', background: 'none',
            fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer',
            color: tab === 'movements' ? 'hsl(var(--color-primary))' : 'hsl(var(--color-text-muted))',
            borderBottom: tab === 'movements' ? '2px solid hsl(var(--color-primary))' : 'none',
          }}
        >
          Movement Ledger (Audit Log)
        </button>
      </div>

      {tab === 'on_hand' ? (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '1rem', borderBottom: '1px solid hsl(var(--color-border))', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={lowStockOnly} onChange={e => setLowStockOnly(e.target.checked)} />
              <AlertTriangle size={15} style={{ color: 'hsl(var(--color-warning))' }} /> Show Low Stock / Reorder Needed Only
            </label>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>Product SKU</th>
                <th>Product Name</th>
                <th>Warehouse</th>
                <th>On Hand</th>
                <th>Reserved</th>
                <th>Available</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map((item: InventoryItem) => {
                const prod = products.find(p => p.id === item.product_id);
                const wh = warehouses.find(w => w.id === item.warehouse_id);
                const onHand = parseFloat(item.quantity_on_hand);
                const reserved = parseFloat(item.quantity_reserved);
                const available = onHand - reserved;
                const reorderPt = parseFloat(prod?.reorder_point || '0');

                const statusBadge = onHand <= 0 ? 'badge-danger' : onHand <= reorderPt ? 'badge-warning' : 'badge-success';
                const statusText = onHand <= 0 ? 'STOCKOUT' : onHand <= reorderPt ? 'LOW STOCK' : 'IN STOCK';

                return (
                  <tr key={item.id}>
                    <td><code style={{ color: 'hsl(var(--color-primary))', fontWeight: 600 }}>{prod?.sku || item.product_id.slice(0, 8)}</code></td>
                    <td style={{ fontWeight: 600, color: 'hsl(var(--color-text-primary))' }}>{prod?.name || '—'}</td>
                    <td>{wh?.name || '—'}</td>
                    <td style={{ fontWeight: 700 }}>{onHand.toLocaleString()}</td>
                    <td>{reserved.toLocaleString()}</td>
                    <td style={{ fontWeight: 700, color: available > 0 ? 'hsl(var(--color-success))' : 'hsl(var(--color-danger))' }}>{available.toLocaleString()}</td>
                    <td><span className={`badge ${statusBadge}`}>{statusText}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Type</th>
                <th>Quantity</th>
                <th>Reference</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {movements.map((m: InventoryMovement) => {
                const typeBadge = m.movement_type === 'IN' ? 'badge-success' : m.movement_type === 'OUT' ? 'badge-danger' : 'badge-info';
                return (
                  <tr key={m.id}>
                    <td style={{ fontSize: '0.8rem', color: 'hsl(var(--color-text-muted))' }}>{new Date(m.created_at).toLocaleString()}</td>
                    <td><span className={`badge ${typeBadge}`}>{m.movement_type}</span></td>
                    <td style={{ fontWeight: 700 }}>{parseFloat(m.quantity).toLocaleString()}</td>
                    <td><span className="badge badge-neutral">{m.reference_type || 'MANUAL'}</span></td>
                    <td>{m.reason || '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Adjust Modal */}
      {showAdjustModal && (
        <div className="modal-overlay" onClick={() => setShowAdjustModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', marginBottom: '1.25rem' }}>Manual Stock Adjustment</h2>
            <form onSubmit={e => { e.preventDefault(); adjustMutation.mutate(adjustForm); }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Product *</label>
                <select className="form-input" required value={adjustForm.product_id} onChange={e => setAdjustForm({ ...adjustForm, product_id: e.target.value })}>
                  <option value="">Select Product</option>
                  {products.map((p: Product) => (<option key={p.id} value={p.id}>{p.sku} - {p.name}</option>))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Warehouse *</label>
                <select className="form-input" required value={adjustForm.warehouse_id} onChange={e => setAdjustForm({ ...adjustForm, warehouse_id: e.target.value })}>
                  <option value="">Select Warehouse</option>
                  {warehouses.map((w: Warehouse) => (<option key={w.id} value={w.id}>{w.name}</option>))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Adjustment Quantity (+ to add, - to remove) *</label>
                <input className="form-input" type="number" required value={adjustForm.quantity} onChange={e => setAdjustForm({ ...adjustForm, quantity: parseFloat(e.target.value) || 0 })} />
              </div>
              <div className="form-group">
                <label className="form-label">Reason</label>
                <input className="form-input" value={adjustForm.reason} onChange={e => setAdjustForm({ ...adjustForm, reason: e.target.value })} placeholder="e.g. Physical count discrepancy" />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAdjustModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={adjustMutation.isPending}>Submit Adjustment</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transfer Modal */}
      {showTransferModal && (
        <div className="modal-overlay" onClick={() => setShowTransferModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', marginBottom: '1.25rem' }}>Inter-Warehouse Transfer</h2>
            <form onSubmit={e => { e.preventDefault(); transferMutation.mutate(transferForm); }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Product *</label>
                <select className="form-input" required value={transferForm.product_id} onChange={e => setTransferForm({ ...transferForm, product_id: e.target.value })}>
                  <option value="">Select Product</option>
                  {products.map((p: Product) => (<option key={p.id} value={p.id}>{p.sku} - {p.name}</option>))}
                </select>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">From Warehouse *</label>
                  <select className="form-input" required value={transferForm.from_warehouse_id} onChange={e => setTransferForm({ ...transferForm, from_warehouse_id: e.target.value })}>
                    <option value="">Select Source</option>
                    {warehouses.map((w: Warehouse) => (<option key={w.id} value={w.id}>{w.name}</option>))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">To Warehouse *</label>
                  <select className="form-input" required value={transferForm.to_warehouse_id} onChange={e => setTransferForm({ ...transferForm, to_warehouse_id: e.target.value })}>
                    <option value="">Select Destination</option>
                    {warehouses.filter(w => w.id !== transferForm.from_warehouse_id).map((w: Warehouse) => (<option key={w.id} value={w.id}>{w.name}</option>))}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Transfer Quantity *</label>
                <input className="form-input" type="number" min="1" required value={transferForm.quantity} onChange={e => setTransferForm({ ...transferForm, quantity: parseFloat(e.target.value) || 0 })} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowTransferModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={transferMutation.isPending}>Execute Transfer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
