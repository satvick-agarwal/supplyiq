import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Tag, Trash2, Edit } from 'lucide-react';
import { categoriesApi } from '@/api';
import type { Category } from '@/types';

export function CategoriesPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [form, setForm] = useState({ name: '', parent_id: '' });

  const { data: catData, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesApi.list({ page_size: 100 }),
  });

  const categories = catData?.data?.items ?? [];

  const saveMutation = useMutation({
    mutationFn: (data: Partial<Category>) =>
      editingCategory ? categoriesApi.update(editingCategory.id, data) : categoriesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      setShowModal(false);
      setEditingCategory(null);
      setForm({ name: '', parent_id: '' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => categoriesApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['categories'] }),
  });

  const handleEdit = (cat: Category) => {
    setEditingCategory(cat);
    setForm({ name: cat.name, parent_id: cat.parent_id || '' });
    setShowModal(true);
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Categories</h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Product taxonomy and classification hierarchy
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => { setEditingCategory(null); setForm({ name: '', parent_id: '' }); setShowModal(true); }}>
          <Plus size={16} /> Add Category
        </button>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading categories...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Category Name</th>
                <th>Parent Category</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((c: Category) => (
                <tr key={c.id}>
                  <td style={{ fontWeight: 600, color: 'hsl(var(--color-text-primary))', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Tag size={16} style={{ color: 'hsl(var(--color-primary))' }} /> {c.name}
                  </td>
                  <td>{categories.find(parent => parent.id === c.parent_id)?.name || 'Top level'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn btn-ghost btn-sm" onClick={() => handleEdit(c)}><Edit size={14} /></button>
                      <button className="btn btn-ghost btn-sm" style={{ color: 'hsl(var(--color-danger))' }} onClick={() => deleteMutation.mutate(c.id)}><Trash2 size={14} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 style={{ fontSize: '1.25rem', fontFamily: 'Outfit', marginBottom: '1.25rem' }}>
              {editingCategory ? 'Edit Category' : 'Add Category'}
            </h2>
            <form onSubmit={e => { e.preventDefault(); saveMutation.mutate(form); }} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Category Name *</label>
                <input className="form-input" required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. Components" />
              </div>
              <div className="form-group">
                <label className="form-label">Parent Category</label>
                <select className="form-input" value={form.parent_id} onChange={e => setForm({ ...form, parent_id: e.target.value })}>
                  <option value="">None (Top level)</option>
                  {categories.filter(c => c.id !== editingCategory?.id).map((c: Category) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
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
