import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Package, Tag, Truck, Warehouse, BarChart3,
  ShoppingCart, ClipboardList, Ship, Users, Bell, Settings,
  ChevronLeft, ChevronRight, Zap, LogOut, UserCircle, AlertTriangle,
  FileText, Brain,
} from 'lucide-react';
import { useAuthStore } from '@/store/auth';
import { authApi } from '@/api';
import { cn } from '@/utils/cn';

const navSections = [
  {
    label: 'Overview',
    items: [
      { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/alerts', icon: AlertTriangle, label: 'Alerts' },
      { to: '/ai-insights', icon: Brain, label: 'AI Insights' },
    ],
  },
  {
    label: 'Catalog',
    items: [
      { to: '/products', icon: Package, label: 'Products' },
      { to: '/categories', icon: Tag, label: 'Categories' },
      { to: '/suppliers', icon: Truck, label: 'Suppliers' },
    ],
  },
  {
    label: 'Operations',
    items: [
      { to: '/warehouses', icon: Warehouse, label: 'Warehouses' },
      { to: '/inventory', icon: BarChart3, label: 'Inventory' },
      { to: '/purchase-orders', icon: ShoppingCart, label: 'Purchase Orders' },
      { to: '/sales-orders', icon: ClipboardList, label: 'Sales Orders' },
      { to: '/shipments', icon: Ship, label: 'Shipments' },
      { to: '/customers', icon: Users, label: 'Customers' },
    ],
  },
  {
    label: 'Admin',
    items: [
      { to: '/reports', icon: FileText, label: 'Reports' },
      { to: '/admin/users', icon: Settings, label: 'User Management' },
    ],
  },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    try { await authApi.logout(); } catch {}
    logout();
    navigate('/login');
  };

  return (
    <aside className={cn('sidebar', collapsed && 'collapsed')}>
      {/* Logo */}
      <div style={{
        padding: '1.25rem 1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        borderBottom: '1px solid hsl(var(--color-border))',
        minHeight: 64,
      }}>
        <div style={{
          width: 36, height: 36,
          background: 'linear-gradient(135deg, hsl(var(--color-primary)), hsl(var(--color-accent)))',
          borderRadius: 10,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <Zap size={18} color="white" />
        </div>
        {!collapsed && (
          <div style={{ overflow: 'hidden' }}>
            <div className="gradient-text" style={{ fontFamily: 'Outfit', fontWeight: 800, fontSize: '1.1rem', lineHeight: 1.2 }}>
              SupplyIQ
            </div>
            <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))', fontWeight: 500 }}>
              Enterprise SCM
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, overflowY: 'auto', padding: '0.75rem 0.625rem' }}>
        {navSections.map((section) => (
          <div key={section.label} style={{ marginBottom: '0.5rem' }}>
            {!collapsed && (
              <div style={{
                fontSize: '0.65rem', fontWeight: 700, letterSpacing: '0.08em',
                textTransform: 'uppercase', color: 'hsl(var(--color-text-muted))',
                padding: '0.5rem 0.5rem 0.25rem',
              }}>
                {section.label}
              </div>
            )}
            {section.items.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  cn('sidebar-nav-item', isActive && 'active')
                }
                title={collapsed ? label : undefined}
              >
                <Icon size={18} style={{ flexShrink: 0 }} />
                {!collapsed && <span>{label}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* User + Collapse */}
      <div style={{ borderTop: '1px solid hsl(var(--color-border))', padding: '0.75rem 0.625rem' }}>
        {!collapsed && user && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.625rem',
            padding: '0.625rem 0.75rem',
            background: 'hsl(var(--color-surface))',
            borderRadius: 'var(--radius-md)',
            marginBottom: '0.5rem',
          }}>
            <div style={{
              width: 32, height: 32,
              background: 'linear-gradient(135deg, hsl(var(--color-primary)), hsl(var(--color-accent)))',
              borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0, fontSize: '0.75rem', fontWeight: 700, color: 'white',
            }}>
              {user.full_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
            </div>
            <div style={{ overflow: 'hidden', flex: 1 }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'hsl(var(--color-text-primary))', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user.full_name}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))' }}>
                {user.role.name}
              </div>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="sidebar-nav-item btn-ghost"
          style={{ width: '100%', border: 'none', background: 'transparent' }}
          title={collapsed ? 'Logout' : undefined}
        >
          <LogOut size={16} style={{ flexShrink: 0 }} />
          {!collapsed && <span>Logout</span>}
        </button>
        <button
          onClick={onToggle}
          className="sidebar-nav-item btn-ghost"
          style={{ width: '100%', border: 'none', background: 'transparent', justifyContent: collapsed ? 'center' : 'flex-start' }}
        >
          {collapsed ? <ChevronRight size={16} /> : <><ChevronLeft size={16} /><span>Collapse</span></>}
        </button>
      </div>
    </aside>
  );
}
