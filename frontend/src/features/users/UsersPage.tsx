import { useQuery } from '@tanstack/react-query';
import { Users, Shield, Mail, CheckCircle } from 'lucide-react';
import { usersApi } from '@/api';
import type { User } from '@/types';

export function UsersPage() {
  const { data: userData, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.list({ page_size: 50 }),
  });

  const users = userData?.data?.items ?? [];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>User Management & RBAC</h1>
        <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
          Role-based access control and system user administration
        </p>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Loading users...</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Full Name</th>
                <th>Email Address</th>
                <th>Assigned Role</th>
                <th>Status</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u: User) => (
                <tr key={u.id}>
                  <td style={{ fontWeight: 600, color: 'hsl(var(--color-text-primary))' }}>{u.full_name}</td>
                  <td>{u.email}</td>
                  <td><span className="badge badge-primary">{u.role.name}</span></td>
                  <td><span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>{u.is_active ? 'Active' : 'Disabled'}</span></td>
                  <td style={{ fontSize: '0.8rem', color: 'hsl(var(--color-text-muted))' }}>{new Date(u.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
