import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Brain, RefreshCw, Sparkles, Filter } from 'lucide-react';
import { aiInsightsApi } from '@/api';
import { formatRelative } from '@/utils/format';
import type { AiInsight } from '@/types';

export function AiInsightsPage() {
  const queryClient = useQueryClient();
  const [filterCat, setFilterCat] = useState<string>('');

  const { data: insightData, isLoading } = useQuery({
    queryKey: ['ai-insights', filterCat],
    queryFn: () => aiInsightsApi.list({ page_size: 50, category: filterCat || undefined }),
  });

  const generateMutation = useMutation({
    mutationFn: () => aiInsightsApi.generate(),
    onSuccess: () => {
      setTimeout(() => queryClient.invalidateQueries({ queryKey: ['ai-insights'] }), 1000);
    },
  });

  const insights = insightData?.data?.items ?? [];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <Brain style={{ color: 'hsl(var(--color-accent))' }} /> AI Insights Engine
          </h1>
          <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
            Rule-first, template-narrated intelligence observations
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <select className="form-input" style={{ width: 160 }} value={filterCat} onChange={e => setFilterCat(e.target.value)}>
            <option value="">All Categories</option>
            <option value="inventory">Inventory</option>
            <option value="supplier">Supplier</option>
            <option value="warehouse">Warehouse</option>
            <option value="financial">Financial</option>
            <option value="sales">Sales</option>
          </select>
          <button className="btn btn-primary" onClick={() => generateMutation.mutate()} disabled={generateMutation.isPending}>
            <Sparkles size={16} /> Re-run Engine
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {isLoading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>Running AI analysis...</div>
        ) : insights.map((item: AiInsight) => {
          const sevClass = item.severity === 'critical' ? 'badge-danger' : item.severity === 'warning' ? 'badge-warning' : 'badge-info';
          return (
            <div key={item.id} className="card" style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: 'hsl(var(--color-accent) / 0.15)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0, color: 'hsl(var(--color-accent))',
              }}>
                <Brain size={20} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                  <span className={`badge ${sevClass}`}>{item.severity}</span>
                  <span className="badge badge-neutral">{item.category}</span>
                  <span style={{ fontSize: '0.75rem', color: 'hsl(var(--color-text-muted))', marginLeft: 'auto' }}>
                    Confidence: {(parseFloat(item.confidence_score || '0.9') * 100).toFixed(0)}% · {formatRelative(item.generated_at)}
                  </span>
                </div>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'hsl(var(--color-text-primary))' }}>
                  {item.insight_text}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
