import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Warehouse, MapPin, BarChart2, Edit, Trash2 } from 'lucide-react';
import { warehousesApi } from '@/api';
import type { Warehouse as WarehouseType } from '@/types';

export function WarehousesPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState<WarehouseType | null>(null);
  const [form, setForm] = useState({ name: '', address: '', capacity_units: '50000' });

  const { data: whData, isLoading } = useQuery({
    queryKey: ['warehouses'],
    queryFn: () => warehousesApi.list({ page_size: 50 }),
  });

  const warehouses = whData?.data?.items ?? [];

  const saveMutation = useMutation({
    mutationFn: (data: Partial<WarehouseType>) =>
      editingWarehouse ? warehousesApi.update(editingWarehouse.id, data) : warehousesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warehouses'] });
      setShowModal(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => warehousesApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['warehouses'] }),
  });

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Warehouses & Facilities</h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Distribution centers, capacity management, and location telemetry
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => { setEditingWarehouse(null); setForm({ name: '', address: '', capacity_units: '50000' }); setShowModal(true); }}>
          <Plus size={16} /> Add Warehouse
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading warehouses...</div>
        ) : warehouses.map((wh: WarehouseType) => {
          const cap = parseFloat(wh.capacity_units || '50000');
          return (
            <div key={wh.id} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 10,
                    background: 'hsl(var(--color-primary) / 0.15)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: 'hsl(var(--color-primary))',
                  }}>
                    <Warehouse size={20} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>{wh.name}</h3>
                    <div style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-muted))', display: 'flex', alignItems: 'center', gap: 4 }}>
                      <MapPin size={12} /> {wh.address || 'Location unassigned'}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                  <button className="btn btn-ghost btn-sm" onClick={() => { setEditingWarehouse(wh); setForm({ name: wh.name, address: wh.address || '', capacity_units: wh.capacity_units || '50000' }); setShowModal(true); }}><Edit size={14} /></button>
                  <button className="btn btn-ghost btn-sm" style={{ color: 'hsl(var(--color-danger))' }} onClick={() => deleteMutation.mutate(wh.id)}><Trash2 size={14} /></button>
                </div>
              </div>

              <div style={{ background: 'hsl(var(--color-surface-elevated))', padding: '0.875rem 1rem', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 4 }}>
                  <span style={{ color: 'hsl(var(--color-text-muted))' }}>Storage Capacity</span>
                  <span style={{ fontWeight: 700 }}>{cap.toLocaleString()} units</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-bar-fill" style={{ width: '65%' }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', marginBottom: '1.25rem' }}>
              {editingWarehouse ? 'Edit Warehouse' : 'Add Warehouse'}
            </h2>
            <form onSubmit={e => { e.preventDefault(); saveMutation.mutate(form); }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Warehouse Name *</label>
                <input className="form-input" required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. East Distribution Center" />
              </div>
              <div className="form-group">
                <label className="form-label">Address</label>
                <input className="form-input" value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} placeholder="123 Logistics Way..." />
              </div>
              <div className="form-group">
                <label className="form-label">Capacity (units)</label>
                <input className="form-input" type="number" value={form.capacity_units} onChange={e => setForm({ ...form, capacity_units: e.target.value })} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saveMutation.isPending}>Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
