// ── Auth / User ────────────────────────────────────────────────────────────────

export interface Permission {
  id: string;
  code: string;
  description?: string;
}

export interface Role {
  id: string;
  name: 'Admin' | 'Manager' | 'Employee';
  description?: string;
  permissions: Permission[];
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  last_login_at?: string;
  role: Role;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ── Pagination ─────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ── Category ───────────────────────────────────────────────────────────────────

export interface Category {
  id: string;
  name: string;
  parent_id?: string;
  created_at: string;
}

// ── Product ────────────────────────────────────────────────────────────────────

export interface Product {
  id: string;
  sku: string;
  name: string;
  description?: string;
  category_id?: string;
  unit_of_measure: string;
  unit_cost: string;
  unit_price: string;
  reorder_point: string;
  reorder_quantity: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ── Supplier ───────────────────────────────────────────────────────────────────

export interface Supplier {
  id: string;
  name: string;
  contact_email?: string;
  contact_phone?: string;
  address?: string;
  payment_terms?: string;
  average_lead_time_days?: number;
  reliability_score?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ── Warehouse ──────────────────────────────────────────────────────────────────

export interface Warehouse {
  id: string;
  name: string;
  address?: string;
  capacity_units?: string;
  manager_id?: string;
  created_at: string;
  updated_at: string;
}

export interface WarehouseUtilization {
  warehouse_id: string;
  warehouse_name: string;
  total_quantity_on_hand: number;
  capacity_units: number;
  utilization_percentage: number;
}

// ── Inventory ──────────────────────────────────────────────────────────────────

export interface InventoryItem {
  id: string;
  product_id: string;
  warehouse_id: string;
  quantity_on_hand: string;
  quantity_reserved: string;
  safety_stock: string;
  product?: Product;
}

export interface InventoryMovement {
  id: string;
  inventory_item_id: string;
  movement_type: 'IN' | 'OUT' | 'TRANSFER' | 'ADJUSTMENT';
  quantity: string;
  reference_type?: 'PO' | 'SO' | 'SHIPMENT' | 'MANUAL';
  reference_id?: string;
  reason?: string;
  created_by?: string;
  created_at: string;
}

// ── Customer ───────────────────────────────────────────────────────────────────

export interface Customer {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  customer_type: 'retail' | 'wholesale';
  created_at: string;
  updated_at: string;
}

// ── Purchase Order ─────────────────────────────────────────────────────────────

export type POStatus = 'draft' | 'approved' | 'sent' | 'partially_received' | 'received' | 'closed' | 'cancelled';

export interface POItem {
  id: string;
  product_id: string;
  quantity_ordered: string;
  quantity_received: string;
  unit_cost: string;
  product?: Product;
}

export interface PurchaseOrder {
  id: string;
  supplier_id: string;
  warehouse_id: string;
  status: POStatus;
  order_date?: string;
  expected_date?: string;
  notes?: string;
  created_by?: string;
  items: POItem[];
  created_at: string;
  updated_at: string;
}

// ── Sales Order ────────────────────────────────────────────────────────────────

export type SOStatus = 'draft' | 'confirmed' | 'fulfilled' | 'shipped' | 'delivered' | 'cancelled';

export interface SOItem {
  id: string;
  product_id: string;
  quantity_ordered: string;
  quantity_fulfilled: string;
  unit_price: string;
  product?: Product;
}

export interface SalesOrder {
  id: string;
  customer_id: string;
  warehouse_id: string;
  status: SOStatus;
  order_date?: string;
  notes?: string;
  created_by?: string;
  items: SOItem[];
  created_at: string;
  updated_at: string;
}

// ── Shipment ───────────────────────────────────────────────────────────────────

export type ShipmentStatus = 'pending' | 'in_transit' | 'delivered' | 'delayed' | 'cancelled';

export interface Shipment {
  id: string;
  shipment_type: 'INBOUND' | 'OUTBOUND';
  reference_type?: 'PO' | 'SO';
  reference_id?: string;
  carrier?: string;
  tracking_number?: string;
  origin?: string;
  destination?: string;
  status: ShipmentStatus;
  expected_date?: string;
  delivered_at?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// ── KPI ────────────────────────────────────────────────────────────────────────

export interface KpiSnapshot {
  id: string;
  kpi_code: string;
  scope_type: 'GLOBAL' | 'WAREHOUSE' | 'CATEGORY' | 'SUPPLIER' | 'PRODUCT';
  scope_id?: string;
  value?: string;
  metadata_?: Record<string, unknown>;
  snapshot_date: string;
}

// ── Alert ──────────────────────────────────────────────────────────────────────

export type AlertSeverity = 'info' | 'warning' | 'critical';
export type AlertStatus = 'open' | 'acknowledged' | 'resolved';

export interface Alert {
  id: string;
  alert_type: string;
  severity: AlertSeverity;
  entity_type?: string;
  entity_id?: string;
  message: string;
  status: AlertStatus;
  created_at: string;
  resolved_at?: string;
}

// ── Notification ───────────────────────────────────────────────────────────────

export interface Notification {
  id: string;
  title: string;
  body?: string;
  is_read: boolean;
  alert_id?: string;
  created_at: string;
}

// ── AI Insight ─────────────────────────────────────────────────────────────────

export type InsightSeverity = 'info' | 'warning' | 'critical';
export type InsightCategory = 'inventory' | 'supplier' | 'warehouse' | 'sales' | 'financial';

export interface AiInsight {
  id: string;
  category: InsightCategory;
  entity_type?: string;
  entity_id?: string;
  insight_text: string;
  confidence_score?: string;
  severity: InsightSeverity;
  generated_at: string;
  model_version?: string;
}

// ── Dashboard ──────────────────────────────────────────────────────────────────

export interface DashboardKpis {
  business_health_score: number;
  supply_chain_efficiency: number;
  revenue_mtd: number;
  cost_mtd: number;
  profit_margin_pct: number;
  monthly_growth_pct: number;
  monthly_growth_meta: { this_month: number; last_month: number };
  inventory_turnover: number;
  dead_stock_pct: number;
  order_fulfillment_rate: number;
}

export interface DashboardData {
  kpis: DashboardKpis;
  alerts_summary: {
    total_open: number;
    critical: number;
    warning: number;
    top_alerts: Alert[];
  };
  ai_insights: AiInsight[];
  operational: {
    open_purchase_orders: number;
    open_sales_orders: number;
    low_stock_items: number;
    warehouse_utilization: Array<{
      id: string;
      name: string;
      utilization_pct: number;
      total_qty: number;
      capacity: number;
    }>;
  };
}
