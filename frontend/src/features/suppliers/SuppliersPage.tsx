import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Truck, Award, Clock, Phone, Mail, Trash2, Edit, ChevronRight } from 'lucide-react';
import { suppliersApi } from '@/api';
import type { Supplier } from '@/types';

export function SuppliersPage() {
  const queryClient = useQueryClient();
  const [selectedSupplierId, setSelectedSupplierId] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);

  const [form, setForm] = useState({
    name: '', contact_email: '', contact_phone: '', address: '',
    payment_terms: 'NET30', average_lead_time_days: 10,
  });

  const { data: supData, isLoading } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersApi.list({ page_size: 50 }),
  });

  const { data: scorecardData } = useQuery({
    queryKey: ['supplier-scorecard', selectedSupplierId],
    queryFn: () => selectedSupplierId ? suppliersApi.scorecard(selectedSupplierId) : null,
    enabled: !!selectedSupplierId,
  });

  const suppliers = supData?.data?.items ?? [];

  const saveMutation = useMutation({
    mutationFn: (data: Partial<Supplier>) =>
      editingSupplier ? suppliersApi.update(editingSupplier.id, data) : suppliersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] });
      setShowModal(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => suppliersApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['suppliers'] }),
  });

  const handleEdit = (s: Supplier) => {
    setEditingSupplier(s);
    setForm({
      name: s.name, contact_email: s.contact_email || '', contact_phone: s.contact_phone || '',
      address: s.address || '', payment_terms: s.payment_terms || 'NET30',
      average_lead_time_days: s.average_lead_time_days || 10,
    });
    setShowModal(true);
  };

  const scorecard = scorecardData?.data;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Suppliers & Scorecards</h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Vendor reliability tracking, lead times, and contact details
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => { setEditingSupplier(null); setShowModal(true); }}>
          <Plus size={16} /> Add Supplier
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selectedSupplierId ? '1fr 1fr' : '1fr', gap: '1.5rem' }}>
        {/* Supplier List */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          {isLoading ? (
            <div style={{ padding: '3rem', textAlign: 'center' }}>Loading suppliers...</div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Supplier Name</th>
                  <th>Payment Terms</th>
                  <th>Avg Lead Time</th>
                  <th>Reliability</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {suppliers.map((s: Supplier) => {
                  const score = parseFloat(s.reliability_score || '75');
                  const scoreBadge = score >= 85 ? 'badge-success' : score >= 70 ? 'badge-warning' : 'badge-danger';
                  return (
                    <tr
                      key={s.id}
                      style={{ cursor: 'pointer', background: selectedSupplierId === s.id ? 'hsl(var(--color-primary) / 0.1)' : undefined }}
                      onClick={() => setSelectedSupplierId(s.id)}
                    >
                      <td style={{ fontWeight: 600, color: 'hsl(var(--color-text-primary))' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Truck size={16} style={{ color: 'hsl(var(--color-primary))' }} />
                          {s.name}
                        </div>
                      </td>
                      <td><span className="badge badge-neutral">{s.payment_terms || 'NET30'}</span></td>
                      <td>{s.average_lead_time_days ?? 10} days</td>
                      <td><span className={`badge ${scoreBadge}`}>{score.toFixed(1)}%</span></td>
                      <td onClick={e => e.stopPropagation()}>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button className="btn btn-ghost btn-sm" onClick={() => handleEdit(s)}><Edit size={14} /></button>
                          <button className="btn btn-ghost btn-sm" style={{ color: 'hsl(var(--color-danger))' }} onClick={() => deleteMutation.mutate(s.id)}><Trash2 size={14} /></button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Scorecard Side Panel */}
        {selectedSupplierId && scorecard && (
          <div className="card animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800 }}>{scorecard.supplier_name}</h3>
                <p style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-muted))' }}>Supplier Performance Scorecard</p>
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => setSelectedSupplierId(null)}>✕</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              <div style={{ background: 'hsl(var(--color-surface-elevated))', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <Award size={20} style={{ color: 'hsl(var(--color-primary))', marginBottom: 4 }} />
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'hsl(var(--color-primary))' }}>{scorecard.reliability_score.toFixed(1)}%</div>
                <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))' }}>Reliability Score</div>
              </div>
              <div style={{ background: 'hsl(var(--color-surface-elevated))', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <Clock size={20} style={{ color: 'hsl(var(--color-accent))', marginBottom: 4 }} />
                <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>{scorecard.average_lead_time_days || 10}d</div>
                <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))' }}>Avg Lead Time</div>
              </div>
              <div style={{ background: 'hsl(var(--color-surface-elevated))', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <Truck size={20} style={{ color: 'hsl(var(--color-success))', marginBottom: 4 }} />
                <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>{scorecard.total_purchase_orders}</div>
                <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))' }}>Total POs</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', marginBottom: '1.25rem' }}>
              {editingSupplier ? 'Edit Supplier' : 'Add Supplier'}
            </h2>
            <form onSubmit={e => { e.preventDefault(); saveMutation.mutate(form); }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Supplier Name *</label>
                <input className="form-input" required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. Acme Components Ltd" />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input className="form-input" type="email" value={form.contact_email} onChange={e => setForm({ ...form, contact_email: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Phone</label>
                  <input className="form-input" value={form.contact_phone} onChange={e => setForm({ ...form, contact_phone: e.target.value })} />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Payment Terms</label>
                  <select className="form-input" value={form.payment_terms} onChange={e => setForm({ ...form, payment_terms: e.target.value })}>
                    <option value="COD">COD</option>
                    <option value="NET15">NET15</option>
                    <option value="NET30">NET30</option>
                    <option value="NET45">NET45</option>
                    <option value="NET60">NET60</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Avg Lead Time (days)</label>
                  <input className="form-input" type="number" value={form.average_lead_time_days} onChange={e => setForm({ ...form, average_lead_time_days: parseInt(e.target.value) || 10 })} />
                </div>
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
