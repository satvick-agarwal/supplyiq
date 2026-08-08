import { useState } from 'react';
import { FileText, Download, BarChart2, DollarSign, Package } from 'lucide-react';

export function ReportsPage() {
  const [downloading, setDownloading] = useState<string | null>(null);

  const reports = [
    { id: 'inventory-valuation', title: 'Inventory Valuation Report', desc: 'Current on-hand inventory itemized with unit cost and extended value', icon: Package },
    { id: 'supplier-performance', title: 'Supplier Reliability & Lead Time Report', desc: 'Vendor scorecards, on-time delivery percentages, and lead time variance', icon: BarChart2 },
    { id: 'sales-cogs', title: 'Sales & COGS Profitability Analysis', desc: 'Revenue, cost of goods sold, and gross profit margin broken down by SKU and category', icon: DollarSign },
  ];

  const handleDownload = (id: string) => {
    setDownloading(id);
    setTimeout(() => {
      setDownloading(null);
      alert(`Report '${id}' generated and downloaded successfully.`);
    }, 1200);
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h1 style={{ fontFamily: 'Outfit', fontSize: '1.75rem', fontWeight: 800 }}>Reports & Data Export</h1>
        <p style={{ color: 'hsl(var(--color-text-muted))', fontSize: '0.875rem' }}>
          Operational and financial supply chain intelligence reports
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {reports.map(({ id, title, desc, icon: Icon }) => (
          <div key={id} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1.25rem' }}>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
              <div style={{
                width: 44, height: 44, borderRadius: 12,
                background: 'hsl(var(--color-primary) / 0.15)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'hsl(var(--color-primary))', flexShrink: 0,
              }}>
                <Icon size={22} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: 4 }}>{title}</h3>
                <p style={{ fontSize: '0.8rem', color: 'hsl(var(--color-text-muted))', lineHeight: 1.5 }}>{desc}</p>
              </div>
            </div>

            <button
              className="btn btn-secondary"
              onClick={() => handleDownload(id)}
              disabled={downloading === id}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              <Download size={16} />
              {downloading === id ? 'Generating CSV...' : 'Export to CSV'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
