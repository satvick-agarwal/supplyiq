import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, BarChart, Bar, RadialBarChart, RadialBar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend,
} from 'recharts';
import {
  TrendingUp, TrendingDown, Minus, Package, ShoppingCart,
  AlertTriangle, Warehouse, Brain, RefreshCw, ArrowRight,
  DollarSign, BarChart3, Zap, Activity,
} from 'lucide-react';
import { dashboardApi, kpisApi } from '@/api';
import { formatCurrency, formatPercent, formatNumber, formatRelative } from '@/utils/format';
import type { DashboardData, AiInsight, Alert } from '@/types';
import { useNavigate } from 'react-router-dom';

// ── Helpers ────────────────────────────────────────────────────────────────────
const CHART_COLORS = {
  primary: '#4f8ef7',
  accent: '#8b5cf6',
  success: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  teal: '#14b8a6',
};

function TrendBadge({ value }: { value: number }) {
  if (value > 0) return <span className="trend-up" style={{ display: 'flex', alignItems: 'center', gap: 2, fontSize: '0.8rem', fontWeight: 600 }}><TrendingUp size={13} />+{formatPercent(value)}</span>;
  if (value < 0) return <span className="trend-down" style={{ display: 'flex', alignItems: 'center', gap: 2, fontSize: '0.8rem', fontWeight: 600 }}><TrendingDown size={13} />{formatPercent(value)}</span>;
  return <span className="trend-neutral" style={{ display: 'flex', alignItems: 'center', gap: 2, fontSize: '0.8rem' }}><Minus size={13} />0%</span>;
}

function SeverityDot({ severity }: { severity: string }) {
  return <span className={`severity-dot ${severity}`} />;
}

// ── Health Score Gauge ─────────────────────────────────────────────────────────
function HealthGauge({ value, label, color }: { value: number; label: string; color: string }) {
  const data = [{ value, fill: color }, { value: 100 - value, fill: 'hsl(var(--color-border))' }];
  return (
    <div style={{ textAlign: 'center', position: 'relative', width: 160 }}>
      <ResponsiveContainer width={160} height={120}>
        <RadialBarChart cx={80} cy={90} innerRadius={55} outerRadius={75} startAngle={180} endAngle={0} data={data} barSize={12}>
          <RadialBar dataKey="value" cornerRadius={6} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div style={{ position: 'absolute', bottom: 18, left: 0, right: 0 }}>
        <div style={{ fontSize: '1.6rem', fontWeight: 800, fontFamily: 'Outfit', color }}>{value.toFixed(0)}</div>
        <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))', fontWeight: 600 }}>{label}</div>
      </div>
    </div>
  );
}

// ── KPI Card ───────────────────────────────────────────────────────────────────
function KpiCard({
  label, value, trend, icon: Icon, color, subtitle, onClick,
}: {
  label: string; value: string; trend?: number; icon: React.ElementType;
  color: string; subtitle?: string; onClick?: () => void;
}) {
  return (
    <div className="kpi-card" onClick={onClick} style={{ cursor: onClick ? 'pointer' : 'default' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'hsl(var(--color-text-muted))', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {label}
        </div>
        <div style={{ width: 32, height: 32, borderRadius: 8, background: `${color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Icon size={15} style={{ color }} />
        </div>
      </div>
      <div className="animate-count-up" style={{ fontSize: '1.6rem', fontWeight: 800, fontFamily: 'Outfit', color: 'hsl(var(--color-text-primary))', lineHeight: 1, marginBottom: '0.375rem' }}>
        {value}
      </div>
      {(trend !== undefined || subtitle) && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {trend !== undefined && <TrendBadge value={trend} />}
          {subtitle && <span style={{ fontSize: '0.72rem', color: 'hsl(var(--color-text-muted))' }}>{subtitle}</span>}
        </div>
      )}
    </div>
  );
}

// ── Insight Card ───────────────────────────────────────────────────────────────
function InsightCard({ insight }: { insight: AiInsight }) {
  const sevColors: Record<string, string> = {
    critical: CHART_COLORS.danger,
    warning: CHART_COLORS.warning,
    info: CHART_COLORS.primary,
  };
  const color = sevColors[insight.severity] ?? CHART_COLORS.primary;

  return (
    <div style={{
      padding: '0.875rem 1rem',
      background: 'hsl(var(--color-surface-elevated))',
      borderRadius: 'var(--radius-md)',
      borderLeft: `3px solid ${color}`,
      display: 'flex', gap: '0.75rem', alignItems: 'flex-start',
    }}>
      <SeverityDot severity={insight.severity} />
      <div style={{ flex: 1 }}>
        <p style={{ fontSize: '0.8rem', lineHeight: 1.6, color: 'hsl(var(--color-text-secondary))' }}>
          {insight.insight_text}
        </p>
        <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))', marginTop: '0.3rem' }}>
          {formatRelative(insight.generated_at)} · {insight.category}
        </div>
      </div>
    </div>
  );
}

// ── Alert Row ──────────────────────────────────────────────────────────────────
function AlertRow({ alert }: { alert: Alert }) {
  const sevClass: Record<string, string> = { critical: 'badge-danger', warning: 'badge-warning', info: 'badge-info' };
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
      padding: '0.75rem 0',
      borderBottom: '1px solid hsl(var(--color-border))',
    }}>
      <SeverityDot severity={alert.severity} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '0.8rem', color: 'hsl(var(--color-text-primary))', lineHeight: 1.5 }}>
          {alert.message.slice(0, 100)}{alert.message.length > 100 ? '…' : ''}
        </div>
        <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))', marginTop: 2 }}>
          {formatRelative(alert.created_at)}
        </div>
      </div>
      <span className={`badge ${sevClass[alert.severity]}`} style={{ flexShrink: 0 }}>
        {alert.severity}
      </span>
    </div>
  );
}

// ── Warehouse Utilization Bar ──────────────────────────────────────────────────
function WarehouseBar({ name, pct }: { name: string; pct: number }) {
  const colorClass = pct >= 90 ? 'danger' : pct >= 75 ? 'warning' : 'success';
  return (
    <div style={{ marginBottom: '0.875rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 500 }}>{name}</span>
        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: pct >= 90 ? CHART_COLORS.danger : pct >= 75 ? CHART_COLORS.warning : CHART_COLORS.success }}>
          {pct.toFixed(1)}%
        </span>
      </div>
      <div className="progress-bar">
        <div className={`progress-bar-fill ${colorClass}`} style={{ width: `${Math.min(pct, 100)}%` }} />
      </div>
    </div>
  );
}

// ── Main Dashboard ─────────────────────────────────────────────────────────────
export function ExecutiveDashboard() {
  const navigate = useNavigate();

  const { data: dashResp, isLoading, refetch } = useQuery({
    queryKey: ['dashboard', 'executive'],
    queryFn: () => dashboardApi.executive(),
    refetchInterval: 60000,
  });

  const { data: revenueHistory } = useQuery({
    queryKey: ['kpi-history', 'revenue_mtd'],
    queryFn: () => kpisApi.history('revenue_mtd', 30),
  });

  const { data: fulfillmentHistory } = useQuery({
    queryKey: ['kpi-history', 'order_fulfillment_rate'],
    queryFn: () => kpisApi.history('order_fulfillment_rate', 30),
  });

  const dash: DashboardData | undefined = dashResp?.data;

  const revenueChartData = (revenueHistory?.data ?? []).map(s => ({
    date: s.snapshot_date,
    revenue: parseFloat(s.value ?? '0'),
  }));

  const fulfillmentChartData = (fulfillmentHistory?.data ?? []).map(s => ({
    date: s.snapshot_date,
    rate: parseFloat(s.value ?? '0'),
  }));

  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {[...Array(3)].map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 120, borderRadius: 14 }} />
        ))}
      </div>
    );
  }

  const kpis = dash?.kpis;
  const growth = kpis?.monthly_growth_pct ?? 0;

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

      {/* ── Page Header ──────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.25rem' }}>
            Executive Dashboard
          </h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Real-time supply chain intelligence · Updated just now
          </p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => refetch()}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* ── Health Scores ─────────────────────────────────────────────────────── */}
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '2rem', padding: '1.5rem 2rem', flexWrap: 'wrap', justifyContent: 'center' }}>
        <HealthGauge
          value={kpis?.business_health_score ?? 0}
          label="Business Health"
          color={CHART_COLORS.primary}
        />
        <div style={{ width: 1, height: 100, background: 'hsl(var(--color-border))' }} />
        <HealthGauge
          value={kpis?.supply_chain_efficiency ?? 0}
          label="SC Efficiency"
          color={CHART_COLORS.accent}
        />
        <div style={{ width: 1, height: 100, background: 'hsl(var(--color-border))' }} />
        <div style={{ flex: 1, minWidth: 200 }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'hsl(var(--color-text-muted))', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
            Composite Scores
          </div>
          {[
            { label: 'Order Fulfillment Rate', value: kpis?.order_fulfillment_rate ?? 0, color: CHART_COLORS.success },
            { label: 'Inventory Turnover', value: Math.min((kpis?.inventory_turnover ?? 0) / 12 * 100, 100), color: CHART_COLORS.teal },
            { label: 'Profit Margin', value: Math.min((kpis?.profit_margin_pct ?? 0) / 40 * 100, 100), color: CHART_COLORS.warning },
          ].map(item => (
            <div key={item.label} style={{ marginBottom: '0.625rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                <span style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-secondary))' }}>{item.label}</span>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: item.color }}>{item.value.toFixed(1)}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill" style={{ width: `${item.value}%`, background: item.color }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── KPI Strip ─────────────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
        <KpiCard
          label="Revenue MTD"
          value={formatCurrency(kpis?.revenue_mtd ?? 0, 0)}
          trend={growth}
          icon={DollarSign}
          color={CHART_COLORS.success}
          subtitle="Month to date"
          onClick={() => navigate('/sales-orders')}
        />
        <KpiCard
          label="Gross Profit Margin"
          value={formatPercent(kpis?.profit_margin_pct ?? 0)}
          icon={TrendingUp}
          color={CHART_COLORS.primary}
          subtitle="vs 20% target"
        />
        <KpiCard
          label="Inventory Turnover"
          value={`${(kpis?.inventory_turnover ?? 0).toFixed(2)}×`}
          icon={BarChart3}
          color={CHART_COLORS.teal}
          subtitle="Last 30 days"
          onClick={() => navigate('/inventory')}
        />
        <KpiCard
          label="Dead Stock"
          value={formatPercent(kpis?.dead_stock_pct ?? 0)}
          icon={Package}
          color={CHART_COLORS.warning}
          subtitle="of total value"
          onClick={() => navigate('/inventory')}
        />
        <KpiCard
          label="Open POs"
          value={formatNumber(dash?.operational.open_purchase_orders ?? 0)}
          icon={ShoppingCart}
          color={CHART_COLORS.accent}
          subtitle="Awaiting receipt"
          onClick={() => navigate('/purchase-orders')}
        />
        <KpiCard
          label="Open SOs"
          value={formatNumber(dash?.operational.open_sales_orders ?? 0)}
          icon={Activity}
          color={CHART_COLORS.primary}
          subtitle="In progress"
          onClick={() => navigate('/sales-orders')}
        />
        <KpiCard
          label="Low Stock Items"
          value={formatNumber(dash?.operational.low_stock_items ?? 0)}
          icon={AlertTriangle}
          color={CHART_COLORS.danger}
          subtitle="Below reorder point"
          onClick={() => navigate('/inventory?low_stock=true')}
        />
        <KpiCard
          label="Open Alerts"
          value={formatNumber(dash?.alerts_summary.total_open ?? 0)}
          icon={AlertTriangle}
          color={dash?.alerts_summary.critical ? CHART_COLORS.danger : CHART_COLORS.warning}
          subtitle={`${dash?.alerts_summary.critical ?? 0} critical`}
          onClick={() => navigate('/alerts')}
        />
      </div>

      {/* ── Charts Row ────────────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* Revenue Trend */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700 }}>Revenue Trend</h3>
              <p style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-muted))' }}>30-day rolling</p>
            </div>
            <TrendBadge value={growth} />
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={revenueChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--color-border))" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10, fill: 'hsl(var(--color-text-muted))' }}
                tickFormatter={v => v?.slice(5)}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fontSize: 10, fill: 'hsl(var(--color-text-muted))' }}
                tickFormatter={v => `$${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(v: any) => [formatCurrency(v), 'Revenue']}
                contentStyle={{ background: 'hsl(var(--color-surface-elevated))', border: '1px solid hsl(var(--color-border))', borderRadius: 8 }}
                labelStyle={{ color: 'hsl(var(--color-text-muted))', fontSize: 11 }}
              />
              <Line
                type="monotone" dataKey="revenue" stroke={CHART_COLORS.primary}
                strokeWidth={2} dot={false} activeDot={{ r: 4, fill: CHART_COLORS.primary }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Fulfillment Rate Trend */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700 }}>Fulfillment Rate</h3>
              <p style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-muted))' }}>Target: 95%</p>
            </div>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: CHART_COLORS.success }}>
              {formatPercent(kpis?.order_fulfillment_rate ?? 0)}
            </span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={fulfillmentChartData.slice(-14)}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--color-border))" />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: 'hsl(var(--color-text-muted))' }} tickFormatter={v => v?.slice(5)} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 10, fill: 'hsl(var(--color-text-muted))' }} domain={[70, 100]} tickFormatter={v => `${v}%`} />
              <Tooltip
                formatter={(v: any) => [`${parseFloat(v || 0).toFixed(1)}%`, 'Fulfillment']}
                contentStyle={{ background: 'hsl(var(--color-surface-elevated))', border: '1px solid hsl(var(--color-border))', borderRadius: 8 }}
              />
              <Bar dataKey="rate" radius={[4, 4, 0, 0]}>
                {fulfillmentChartData.slice(-14).map((entry, idx) => (
                  <Cell key={idx} fill={entry.rate >= 90 ? CHART_COLORS.success : entry.rate >= 80 ? CHART_COLORS.warning : CHART_COLORS.danger} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Bottom Row ────────────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>

        {/* AI Insights Feed */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Brain size={16} style={{ color: CHART_COLORS.accent }} />
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700 }}>AI Insights</h3>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/ai-insights')}>
              View all <ArrowRight size={13} />
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
            {(dash?.ai_insights ?? []).slice(0, 4).map(insight => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
            {(!dash?.ai_insights || dash.ai_insights.length === 0) && (
              <div className="empty-state" style={{ padding: '2rem' }}>
                <Brain size={32} style={{ opacity: 0.3 }} />
                <p>No insights yet. Run the AI engine to generate insights.</p>
              </div>
            )}
          </div>
        </div>

        {/* Open Alerts */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle size={16} style={{ color: CHART_COLORS.warning }} />
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700 }}>Open Alerts</h3>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              {(dash?.alerts_summary.critical ?? 0) > 0 && (
                <span className="badge badge-danger">{dash?.alerts_summary.critical} critical</span>
              )}
              <button className="btn btn-ghost btn-sm" onClick={() => navigate('/alerts')}>
                <ArrowRight size={13} />
              </button>
            </div>
          </div>
          {(dash?.alerts_summary.top_alerts ?? []).map(alert => (
            <AlertRow key={alert.id} alert={alert} />
          ))}
          {(!dash?.alerts_summary.top_alerts || dash.alerts_summary.top_alerts.length === 0) && (
            <div className="empty-state" style={{ padding: '2rem' }}>
              <span style={{ fontSize: '2rem' }}>✅</span>
              <p>No open alerts. Everything looks healthy!</p>
            </div>
          )}
        </div>

        {/* Warehouse Utilization */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Warehouse size={16} style={{ color: CHART_COLORS.teal }} />
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700 }}>Warehouse Utilization</h3>
            </div>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/warehouses')}>
              <ArrowRight size={13} />
            </button>
          </div>
          <div style={{ marginTop: '0.5rem' }}>
            {(dash?.operational.warehouse_utilization ?? []).map(wh => (
              <WarehouseBar key={wh.id} name={wh.name} pct={wh.utilization_pct} />
            ))}
          </div>
          <div className="divider" />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, fontFamily: 'Outfit', color: CHART_COLORS.primary }}>
                {dash?.operational.open_purchase_orders ?? 0}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))' }}>Open POs</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, fontFamily: 'Outfit', color: CHART_COLORS.danger }}>
                {dash?.operational.low_stock_items ?? 0}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'hsl(var(--color-text-muted))' }}>Low Stock</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
