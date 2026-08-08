import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, Eye, EyeOff, ArrowRight, Shield, TrendingUp, Brain } from 'lucide-react';
import { authApi } from '@/api';
import { useAuthStore } from '@/store/auth';

const FEATURES = [
  { icon: TrendingUp, label: '16+ Live KPIs', desc: 'Real-time business intelligence' },
  { icon: Brain, label: 'AI Insights', desc: 'Template-driven observations' },
  { icon: Shield, label: 'RBAC Security', desc: 'Granular permissions matrix' },
];

export function LoginPage() {
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();

  const [email, setEmail] = useState('admin@supplyiq.com');
  const [password, setPassword] = useState('Admin@123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const { data: tokenData } = await authApi.login(email, password);
      setTokens(tokenData.access_token, tokenData.refresh_token);

      const { data: user } = await authApi.me();
      setUser(user);

      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-bg">
      {/* Floating orbs */}
      <div style={{
        position: 'fixed', width: 600, height: 600, borderRadius: '50%',
        background: 'radial-gradient(circle, hsl(217 91% 60% / 0.08) 0%, transparent 70%)',
        top: '-200px', left: '-200px', pointerEvents: 'none',
      }} />
      <div style={{
        position: 'fixed', width: 400, height: 400, borderRadius: '50%',
        background: 'radial-gradient(circle, hsl(258 90% 66% / 0.08) 0%, transparent 70%)',
        bottom: '0', right: '-100px', pointerEvents: 'none',
      }} />

      <div style={{ display: 'flex', width: '100%', maxWidth: 960, gap: '4rem', alignItems: 'center', padding: '2rem' }}>

        {/* Left panel — branding */}
        <div style={{ flex: 1, display: 'none' }} className="login-left">
          <div className="animate-fade-in">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
              <div style={{
                width: 48, height: 48,
                background: 'linear-gradient(135deg, hsl(var(--color-primary)), hsl(var(--color-accent)))',
                borderRadius: 14, display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Zap size={24} color="white" />
              </div>
              <span className="gradient-text" style={{ fontFamily: 'Outfit', fontWeight: 900, fontSize: '1.75rem' }}>
                SupplyIQ
              </span>
            </div>
            <h2 style={{ fontFamily: 'Outfit', fontSize: '2.25rem', fontWeight: 800, lineHeight: 1.2, marginBottom: '1rem' }}>
              Enterprise Supply Chain<br />
              <span className="gradient-text">Intelligence Platform</span>
            </h2>
            <p style={{ color: 'hsl(var(--color-text-secondary))', fontSize: '1rem', lineHeight: 1.7, marginBottom: '2.5rem' }}>
              Unify procurement, inventory, logistics, and analytics. Surface what needs attention before it becomes a crisis.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {FEATURES.map(({ icon: Icon, label, desc }) => (
                <div key={label} style={{
                  display: 'flex', alignItems: 'center', gap: '1rem',
                  padding: '0.875rem 1.25rem',
                  background: 'hsl(var(--color-surface) / 0.6)',
                  border: '1px solid hsl(var(--color-border))',
                  borderRadius: 'var(--radius-md)',
                }}>
                  <div style={{
                    width: 36, height: 36,
                    background: 'hsl(var(--color-primary) / 0.15)',
                    borderRadius: 8,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    flexShrink: 0,
                  }}>
                    <Icon size={16} style={{ color: 'hsl(var(--color-primary))' }} />
                  </div>
                  <div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 700 }}>{label}</div>
                    <div style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-muted))' }}>{desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right panel — login form */}
        <div style={{ flex: '0 0 440px', width: '100%', maxWidth: 440 }}>
          <div className="glass-strong animate-slide-up" style={{
            padding: '2.5rem',
            borderRadius: 'var(--radius-xl)',
          }}>
            {/* Logo on mobile */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
              <div style={{
                width: 42, height: 42,
                background: 'linear-gradient(135deg, hsl(var(--color-primary)), hsl(var(--color-accent)))',
                borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Zap size={20} color="white" />
              </div>
              <div>
                <div className="gradient-text" style={{ fontFamily: 'Outfit', fontWeight: 900, fontSize: '1.3rem', lineHeight: 1 }}>
                  SupplyIQ
                </div>
                <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))' }}>Enterprise SCM Platform</div>
              </div>
            </div>

            <h1 style={{ fontFamily: 'Outfit', fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.375rem' }}>
              Welcome back
            </h1>
            <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem', marginBottom: '1.75rem' }}>
              Sign in to your workspace
            </p>

            {error && (
              <div style={{
                background: 'hsl(var(--color-danger) / 0.12)',
                border: '1px solid hsl(var(--color-danger) / 0.3)',
                borderRadius: 'var(--radius-md)',
                padding: '0.75rem 1rem',
                fontSize: '0.875rem',
                color: 'hsl(0 84% 75%)',
                marginBottom: '1.25rem',
              }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Email address</label>
                <input
                  type="email"
                  className="form-input"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@company.com"
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label className="form-label">Password</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-input"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    style={{ paddingRight: '2.75rem' }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: 'absolute', right: '0.75rem', top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none', border: 'none', cursor: 'pointer',
                      color: 'hsl(var(--color-text-muted))',
                    }}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={loading}
                style={{ width: '100%', justifyContent: 'center', marginTop: '0.25rem' }}
              >
                {loading ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div style={{ width: 16, height: 16, border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                    Signing in...
                  </span>
                ) : (
                  <>Sign in <ArrowRight size={16} /></>
                )}
              </button>
            </form>

            {/* Demo credentials */}
            <div style={{
              marginTop: '1.5rem',
              padding: '0.875rem 1rem',
              background: 'hsl(var(--color-primary) / 0.08)',
              border: '1px solid hsl(var(--color-primary) / 0.2)',
              borderRadius: 'var(--radius-md)',
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'hsl(var(--color-primary))', marginBottom: '0.375rem' }}>
                Demo Credentials
              </div>
              <div style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-muted))' }}>
                Admin: admin@supplyiq.com / Admin@123<br />
                Manager: manager@supplyiq.com / Manager@123
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
