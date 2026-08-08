import api from './client';
import type {
  PaginatedResponse, Product, Category, Supplier, Warehouse,
  InventoryItem, InventoryMovement, Customer, PurchaseOrder,
  SalesOrder, Shipment, Alert, Notification, AiInsight,
  KpiSnapshot, DashboardData, TokenResponse, User,
} from '@/types';

// ── Auth ───────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),
  refresh: (refresh_token: string) =>
    api.post<TokenResponse>('/auth/refresh', { refresh_token }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get<User>('/auth/me'),
};

// ── Dashboard ──────────────────────────────────────────────────────────────────
export const dashboardApi = {
  executive: () => api.get<DashboardData>('/dashboard/executive'),
};

// ── Products ───────────────────────────────────────────────────────────────────
export const productsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Product>>('/products', { params }),
  get: (id: string) => api.get<Product>(`/products/${id}`),
  create: (data: Partial<Product>) => api.post<Product>('/products', data),
  update: (id: string, data: Partial<Product>) => api.patch<Product>(`/products/${id}`, data),
  delete: (id: string) => api.delete(`/products/${id}`),
};

// ── Categories ─────────────────────────────────────────────────────────────────
export const categoriesApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Category>>('/categories', { params }),
  get: (id: string) => api.get<Category>(`/categories/${id}`),
  create: (data: Partial<Category>) => api.post<Category>('/categories', data),
  update: (id: string, data: Partial<Category>) => api.patch<Category>(`/categories/${id}`, data),
  delete: (id: string) => api.delete(`/categories/${id}`),
};

// ── Suppliers ──────────────────────────────────────────────────────────────────
export const suppliersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Supplier>>('/suppliers', { params }),
  get: (id: string) => api.get<Supplier>(`/suppliers/${id}`),
  create: (data: Partial<Supplier>) => api.post<Supplier>('/suppliers', data),
  update: (id: string, data: Partial<Supplier>) => api.patch<Supplier>(`/suppliers/${id}`, data),
  delete: (id: string) => api.delete(`/suppliers/${id}`),
  scorecard: (id: string) => api.get(`/suppliers/${id}/scorecard`),
};

// ── Warehouses ─────────────────────────────────────────────────────────────────
export const warehousesApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Warehouse>>('/warehouses', { params }),
  get: (id: string) => api.get<Warehouse>(`/warehouses/${id}`),
  create: (data: Partial<Warehouse>) => api.post<Warehouse>('/warehouses', data),
  update: (id: string, data: Partial<Warehouse>) => api.patch<Warehouse>(`/warehouses/${id}`, data),
  delete: (id: string) => api.delete(`/warehouses/${id}`),
  utilization: (id: string) => api.get(`/warehouses/${id}/utilization`),
};

// ── Inventory ──────────────────────────────────────────────────────────────────
export const inventoryApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<InventoryItem>>('/inventory', { params }),
  lowStock: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<InventoryItem>>('/inventory/low-stock', { params }),
  get: (id: string) => api.get<InventoryItem>(`/inventory/${id}`),
  adjust: (data: { product_id: string; warehouse_id: string; quantity: number; reason?: string }) =>
    api.post('/inventory/adjust', data),
  movements: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<InventoryMovement>>('/inventory-movements', { params }),
  transfer: (data: { product_id: string; from_warehouse_id: string; to_warehouse_id: string; quantity: number; reason?: string }) =>
    api.post('/inventory-movements/transfer', data),
};

// ── Purchase Orders ────────────────────────────────────────────────────────────
export const purchaseOrdersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<PurchaseOrder>>('/purchase-orders', { params }),
  get: (id: string) => api.get<PurchaseOrder>(`/purchase-orders/${id}`),
  create: (data: Partial<PurchaseOrder> & { items: unknown[] }) =>
    api.post<PurchaseOrder>('/purchase-orders', data),
  update: (id: string, data: Partial<PurchaseOrder>) =>
    api.patch<PurchaseOrder>(`/purchase-orders/${id}`, data),
  approve: (id: string) => api.post<PurchaseOrder>(`/purchase-orders/${id}/approve`),
  send: (id: string) => api.post<PurchaseOrder>(`/purchase-orders/${id}/send`),
  receive: (id: string, items: Array<{ product_id: string; quantity_received: number }>) =>
    api.post<PurchaseOrder>(`/purchase-orders/${id}/receive`, { items }),
  cancel: (id: string) => api.post<PurchaseOrder>(`/purchase-orders/${id}/cancel`),
  close: (id: string) => api.post<PurchaseOrder>(`/purchase-orders/${id}/close`),
};

// ── Sales Orders ───────────────────────────────────────────────────────────────
export const salesOrdersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<SalesOrder>>('/sales-orders', { params }),
  get: (id: string) => api.get<SalesOrder>(`/sales-orders/${id}`),
  create: (data: Partial<SalesOrder> & { items: unknown[] }) =>
    api.post<SalesOrder>('/sales-orders', data),
  update: (id: string, data: Partial<SalesOrder>) =>
    api.patch<SalesOrder>(`/sales-orders/${id}`, data),
  confirm: (id: string) => api.post<SalesOrder>(`/sales-orders/${id}/confirm`),
  fulfill: (id: string) => api.post<SalesOrder>(`/sales-orders/${id}/fulfill`),
  ship: (id: string) => api.post<SalesOrder>(`/sales-orders/${id}/ship`),
  cancel: (id: string) => api.post<SalesOrder>(`/sales-orders/${id}/cancel`),
};

// ── Customers ──────────────────────────────────────────────────────────────────
export const customersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Customer>>('/customers', { params }),
  get: (id: string) => api.get<Customer>(`/customers/${id}`),
  create: (data: Partial<Customer>) => api.post<Customer>('/customers', data),
  update: (id: string, data: Partial<Customer>) => api.patch<Customer>(`/customers/${id}`, data),
  delete: (id: string) => api.delete(`/customers/${id}`),
  orders: (id: string) => api.get<PaginatedResponse<SalesOrder>>(`/customers/${id}/orders`),
};

// ── Shipments ──────────────────────────────────────────────────────────────────
export const shipmentsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Shipment>>('/shipments', { params }),
  get: (id: string) => api.get<Shipment>(`/shipments/${id}`),
  create: (data: Partial<Shipment>) => api.post<Shipment>('/shipments', data),
  updateStatus: (id: string, status: string, notes?: string) =>
    api.post<Shipment>(`/shipments/${id}/status`, { status, notes }),
};

// ── Alerts ─────────────────────────────────────────────────────────────────────
export const alertsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Alert>>('/alerts', { params }),
  update: (id: string, status: string) =>
    api.patch<Alert>(`/alerts/${id}`, { status }),
};

// ── Notifications ──────────────────────────────────────────────────────────────
export const notificationsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Notification>>('/notifications', { params }),
  markRead: (id: string) => api.patch(`/notifications/${id}/read`),
  markAllRead: () => api.patch('/notifications/mark-all-read'),
};

// ── AI Insights ────────────────────────────────────────────────────────────────
export const aiInsightsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<AiInsight>>('/ai-insights', { params }),
  dashboardSummary: () => api.get<AiInsight[]>('/ai-insights/dashboard-summary'),
  generate: () => api.post('/ai-insights/generate'),
};

// ── KPIs ───────────────────────────────────────────────────────────────────────
export const kpisApi = {
  latest: () => api.get<Record<string, KpiSnapshot | null>>('/kpis/latest'),
  history: (code: string, days = 30, scopeId?: string) =>
    api.get<KpiSnapshot[]>(`/kpis/${code}/history`, { params: { days, scope_id: scopeId } }),
  recompute: () => api.post('/kpis/recompute'),
};

// ── Users ──────────────────────────────────────────────────────────────────────
export const usersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<User>>('/users', { params }),
  get: (id: string) => api.get<User>(`/users/${id}`),
  create: (data: { email: string; password: string; full_name: string; role_id: string }) =>
    api.post<User>('/users', data),
  update: (id: string, data: Partial<User>) => api.patch<User>(`/users/${id}`, data),
  delete: (id: string) => api.delete(`/users/${id}`),
};
