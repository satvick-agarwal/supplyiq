export function formatCurrency(value: number | string, decimals = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num || 0);
}

export function formatNumber(value: number | string, decimals = 0): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num || 0);
}

export function formatPercent(value: number | string, decimals = 1): string {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return `${(num || 0).toFixed(decimals)}%`;
}

export function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

export function formatDateTime(dateStr: string | undefined): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export function formatRelative(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return formatDate(dateStr);
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen) + '…';
}

export function poStatusColor(status: string): string {
  const map: Record<string, string> = {
    draft: 'neutral', approved: 'info', sent: 'primary',
    partially_received: 'warning', received: 'success',
    closed: 'neutral', cancelled: 'danger',
  };
  return map[status] ?? 'neutral';
}

export function soStatusColor(status: string): string {
  const map: Record<string, string> = {
    draft: 'neutral', confirmed: 'info', fulfilled: 'primary',
    shipped: 'warning', delivered: 'success', cancelled: 'danger',
  };
  return map[status] ?? 'neutral';
}

export function shipmentStatusColor(status: string): string {
  const map: Record<string, string> = {
    pending: 'neutral', in_transit: 'info',
    delivered: 'success', delayed: 'danger', cancelled: 'neutral',
  };
  return map[status] ?? 'neutral';
}
