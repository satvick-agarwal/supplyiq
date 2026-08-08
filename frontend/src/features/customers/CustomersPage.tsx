import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, Mail, Phone, MapPin, Search } from 'lucide-react';
import { customersApi } from '@/api';
import type { Customer } from '@/types';

export function CustomersPage() {
  const [search, setSearch] = useState('');
  const { data: custData, isLoading } = useQuery({
    queryKey: ['customers', search],
    queryFn: () => customersApi.list({ page_size: 50, search: search || undefined }),
  });

  const customers = custData?.data?.items ?? [];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Customers Directory</h1>
        <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
          Retail and wholesale customer accounts and contact info
        </p>
      </div>

      <div className="card" style={{ padding: '1rem' }}>
        <input className="form-input" placeholder="Search customers..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading customers...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Customer Name</th>
                <th>Type</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Address</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c: Customer) => (
                <tr key={c.id}>
                  <td style={{ fontWeight: 600, color: 'hsl(var(--color-text-primary))' }}>{c.name}</td>
                  <td><span className="badge badge-primary">{c.customer_type}</span></td>
                  <td>{c.email || '—'}</td>
                  <td>{c.phone || '—'}</td>
                  <td style={{ fontSize: '0.8rem', color: 'hsl(var(--color-text-muted))' }}>{c.address || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
