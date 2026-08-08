import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Filter, Trash2, Edit, AlertCircle, Package } from 'lucide-react';
import { productsApi, categoriesApi } from '@/api';
import { formatCurrency, formatDate } from '@/utils/format';
import type { Product, Category } from '@/types';

export function ProductsPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [selectedCat, setSelectedCat] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  // Form state
  const [form, setForm] = useState({
    sku: '', name: '', description: '', category_id: '',
    unit_of_measure: 'unit', unit_cost: '', unit_price: '',
    reorder_point: '', reorder_quantity: '',
  });

  const { data: prodData, isLoading } = useQuery({
    queryKey: ['products', page, search, selectedCat],
    queryFn: () => productsApi.list({ page, page_size: 15, search: search || undefined, category_id: selectedCat || undefined }),
  });

  const { data: catData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesApi.list({ page_size: 100 }),
  });

  const categories = catData?.data?.items ?? [];
  const products = prodData?.data?.items ?? [];
  const totalPages = Math.ceil((prodData?.data?.total ?? 0) / 15);

  const saveMutation = useMutation({
    mutationFn: (data: Partial<Product>) =>
      editingProduct ? productsApi.update(editingProduct.id, data) : productsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      setShowModal(false);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => productsApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['products'] }),
  });

  const resetForm = () => {
    setEditingProduct(null);
    setForm({
      sku: '', name: '', description: '', category_id: '',
      unit_of_measure: 'unit', unit_cost: '', unit_price: '',
      reorder_point: '', reorder_quantity: '',
    });
  };

  const handleEdit = (prod: Product) => {
    setEditingProduct(prod);
    setForm({
      sku: prod.sku, name: prod.name, description: prod.description || '',
      category_id: prod.category_id || '', unit_of_measure: prod.unit_of_measure,
      unit_cost: prod.unit_cost, unit_price: prod.unit_price,
      reorder_point: prod.reorder_point, reorder_quantity: prod.reorder_quantity,
    });
    setShowModal(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveMutation.mutate({
      ...form,
      unit_cost: form.unit_cost,
      unit_price: form.unit_price,
      reorder_point: form.reorder_point,
      reorder_quantity: form.reorder_quantity,
    });
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Product Catalog</h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Manage SKUs, pricing, reorder points, and categories
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
          <Plus size={16} /> Add Product
        </button>
      </div>

      {/* Filters */}
      <div className="card" style={{ padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: 240 }}>
          <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'hsl(var(--color-text-muted))' }} />
          <input
            type="text"
            className="form-input"
            placeholder="Search by SKU or name..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: '2.5rem' }}
          />
        </div>
        <select
          className="form-input"
          style={{ width: 200 }}
          value={selectedCat}
          onChange={e => setSelectedCat(e.target.value)}
        >
          <option value="">All Categories</option>
          {categories.map((c: Category) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* Product Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading products...</div>
        ) : products.length === 0 ? (
          <div className="empty-state">
            <Package size={40} style={{ opacity: 0.3 }} />
            <p>No products found</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Name</th>
                <th>Category</th>
                <th>UOM</th>
                <th>Unit Cost</th>
                <th>Unit Price</th>
                <th>Reorder Pt</th>
                <th>Reorder Qty</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p: Product) => (
                <tr key={p.id}>
                  <td><code style={{ fontSize: '0.8rem', color: 'hsl(var(--color-primary))', fontWeight: 600 }}>{p.sku}</code></td>
                  <td style={{ fontWeight: 600, color: 'hsl(var(--color-text-primary))' }}>{p.name}</td>
                  <td>{categories.find(c => c.id === p.category_id)?.name || '—'}</td>
                  <td><span className="badge badge-neutral">{p.unit_of_measure}</span></td>
                  <td>{formatCurrency(p.unit_cost)}</td>
                  <td style={{ fontWeight: 600, color: 'hsl(var(--color-success))' }}>{formatCurrency(p.unit_price)}</td>
                  <td>{parseFloat(p.reorder_point).toLocaleString()}</td>
                  <td>{parseFloat(p.reorder_quantity).toLocaleString()}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => handleEdit(p)} title="Edit"><Edit size={14} /></button>
                      <button className="btn btn-ghost btn-sm" style={{ color: 'hsl(var(--color-danger))' }} onClick={() => deleteMutation.mutate(p.id)} title="Delete"><Trash2 size={14} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem' }}>
          <button className="btn btn-secondary btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Prev</button>
          <span style={{ fontSize: '0.875rem', alignSelf: 'center', color: 'hsl(var(--color-text-muted))' }}>Page {page} of {totalPages}</span>
          <button className="btn btn-secondary btn-sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next</button>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', marginBottom: '1.25rem' }}>
              {editingProduct ? 'Edit Product' : 'Add New Product'}
            </h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">SKU *</label>
                  <input className="form-input" required value={form.sku} onChange={e => setForm({ ...form, sku: e.target.value })} placeholder="e.g. MICRO-328P" />
                </div>
                <div className="form-group">
                  <label className="form-label">Product Name *</label>
                  <input className="form-input" required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. ATmega328P Microcontroller" />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Category</label>
                <select className="form-input" value={form.category_id} onChange={e => setForm({ ...form, category_id: e.target.value })}>
                  <option value="">Select Category</option>
                  {categories.map((c: Category) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Unit of Measure</label>
                  <input className="form-input" value={form.unit_of_measure} onChange={e => setForm({ ...form, unit_of_measure: e.target.value })} placeholder="unit, pack, ream..." />
                </div>
                <div className="form-group">
                  <label className="form-label">Unit Cost ($) *</label>
                  <input className="form-input" type="number" step="0.01" required value={form.unit_cost} onChange={e => setForm({ ...form, unit_cost: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Unit Price ($) *</label>
                  <input className="form-input" type="number" step="0.01" required value={form.unit_price} onChange={e => setForm({ ...form, unit_price: e.target.value })} />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Reorder Point *</label>
                  <input className="form-input" type="number" required value={form.reorder_point} onChange={e => setForm({ ...form, reorder_point: e.target.value })} />
                </div>
                <div className="form-group">
                  <label className="form-label">Reorder Quantity *</label>
                  <input className="form-input" type="number" required value={form.reorder_quantity} onChange={e => setForm({ ...form, reorder_quantity: e.target.value })} />
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saveMutation.isPending}>
                  {saveMutation.isPending ? 'Saving...' : 'Save Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
