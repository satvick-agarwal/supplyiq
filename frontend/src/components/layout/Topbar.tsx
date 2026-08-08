import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Search, ChevronDown, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { notificationsApi } from '@/api';
import { useAuthStore } from '@/store/auth';
import { formatDistanceToNow } from 'date-fns';
import type { Notification } from '@/types';

interface TopbarProps {
  title?: string;
}

export function Topbar({ title }: TopbarProps) {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [showNotifs, setShowNotifs] = useState(false);

  const { data: notifData, refetch } = useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: () => notificationsApi.list({ unread_only: true, page_size: 8 }),
    refetchInterval: 30000, // poll every 30s
  });

  const notifications = notifData?.data?.items ?? [];
  const unreadCount = notifData?.data?.total ?? 0;

  const handleMarkRead = async (id: string) => {
    await notificationsApi.markRead(id);
    refetch();
  };

  return (
    <header className="topbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {title && (
          <h1 style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'Outfit', color: 'hsl(var(--color-text-primary))' }}>
            {title}
          </h1>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Notification Bell */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            className="btn btn-ghost btn-sm"
            style={{ position: 'relative', padding: '0.5rem' }}
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute', top: 2, right: 2,
                background: 'hsl(var(--color-danger))',
                color: 'white', fontSize: '0.6rem', fontWeight: 700,
                width: 16, height: 16, borderRadius: '50%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                animation: 'pulse 2s infinite',
              }}>
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {showNotifs && (
            <>
              <div onClick={() => setShowNotifs(false)} style={{ position: 'fixed', inset: 0, zIndex: 90 }} />
              <div style={{
                position: 'absolute', top: '100%', right: 0, marginTop: 8,
                background: 'hsl(var(--color-surface))',
                border: '1px solid hsl(var(--color-border-bright))',
                borderRadius: 'var(--radius-lg)',
                width: 360, maxHeight: 480, overflowY: 'auto',
                zIndex: 100,
                boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
              }}>
                <div style={{
                  padding: '1rem 1.25rem',
                  borderBottom: '1px solid hsl(var(--color-border))',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                }}>
                  <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>Notifications</span>
                  {unreadCount > 0 && (
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={async () => { await notificationsApi.markAllRead(); refetch(); }}
                      style={{ fontSize: '0.75rem' }}
                    >
                      Mark all read
                    </button>
                  )}
                </div>
                {notifications.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
                    No unread notifications
                  </div>
                ) : (
                  notifications.map((n: Notification) => (
                    <div
                      key={n.id}
                      onClick={() => handleMarkRead(n.id)}
                      style={{
                        padding: '0.875rem 1.25rem',
                        borderBottom: '1px solid hsl(var(--color-border))',
                        cursor: 'pointer',
                        transition: 'background 0.15s',
                        background: n.is_read ? 'transparent' : 'hsl(var(--color-primary) / 0.05)',
                      }}
                      onMouseEnter={e => (e.currentTarget.style.background = 'hsl(var(--color-surface-elevated))')}
                      onMouseLeave={e => (e.currentTarget.style.background = n.is_read ? 'transparent' : 'hsl(var(--color-primary) / 0.05)')}
                    >
                      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                        {!n.is_read && (
                          <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'hsl(var(--color-primary))', marginTop: 6, flexShrink: 0 }} />
                        )}
                        <div>
                          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'hsl(var(--color-text-primary))' }}>{n.title}</div>
                          {n.body && <div style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-muted))', marginTop: 2, lineHeight: 1.5 }}>{n.body.slice(0, 100)}...</div>}
                          <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))', marginTop: 4 }}>
                            {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div style={{ padding: '0.75rem 1.25rem', textAlign: 'center' }}>
                  <button className="btn btn-ghost btn-sm" onClick={() => { navigate('/alerts'); setShowNotifs(false); }}>
                    View all alerts →
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        {/* User avatar */}
        {user && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            padding: '0.375rem 0.75rem',
            background: 'hsl(var(--color-surface))',
            borderRadius: 'var(--radius-md)',
            border: '1px solid hsl(var(--color-border))',
            fontSize: '0.8rem', fontWeight: 500,
            cursor: 'pointer',
          }}>
            <div style={{
              width: 26, height: 26,
              background: 'linear-gradient(135deg, hsl(var(--color-primary)), hsl(var(--color-accent)))',
              borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.65rem', fontWeight: 700, color: 'white',
            }}>
              {user.full_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
            </div>
            <span style={{ color: 'hsl(var(--color-text-secondary))' }}>{user.full_name.split(' ')[0]}</span>
            <span className="badge badge-primary" style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem' }}>{user.role.name}</span>
          </div>
        )}
      </div>
    </header>
  );
}
