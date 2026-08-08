# SupplyIQ — Enterprise Supply Chain Intelligence Platform
### Implementation-Ready Product Design Document
Version 1.0 · Prepared for autonomous build execution (Antigravity-compatible)

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Business Problem](#2-business-problem)
3. [Product Vision](#3-product-vision)
4. [User Personas](#4-user-personas)
5. [Complete Feature List](#5-complete-feature-list)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [Detailed Module Breakdown](#8-detailed-module-breakdown)
9. [User Workflows](#9-user-workflows)
10. [Database Design](#10-database-design)
11. [ER Diagram Description](#11-er-diagram-description)
12. [API Architecture](#12-api-architecture)
13. [REST Endpoint List](#13-rest-endpoint-list)
14. [Backend Folder Structure](#14-backend-folder-structure)
15. [Frontend Folder Structure](#15-frontend-folder-structure)
16. [Microservice vs Monolith Discussion](#16-microservice-vs-monolith-discussion)
17. [Authentication Flow](#17-authentication-flow)
18. [Inventory Workflow](#18-inventory-workflow)
19. [Procurement Workflow](#19-procurement-workflow)
20. [Shipment Workflow](#20-shipment-workflow)
21. [Dashboard Design](#21-dashboard-design)
22. [KPI Definitions](#22-kpi-definitions)
23. [AI Insight Engine Design](#23-ai-insight-engine-design)
24. [Recommended Charts](#24-recommended-charts)
25. [Permissions Matrix](#25-permissions-matrix)
26. [Development Roadmap](#26-development-roadmap)
27. [Future Enhancements](#27-future-enhancements)
28. [Resume-Worthy Features](#28-resume-worthy-features)

---

## 1. Product Overview

**SupplyIQ** is an enterprise-grade Supply Chain Intelligence Platform that unifies procurement, inventory, warehousing, logistics, supplier relationships, and executive analytics into a single operational and decision-support system. It is not a CRUD inventory tracker — it is a **decision intelligence layer** sitting on top of core supply chain operations, generating derived metrics, predictive signals, and narrative AI insights that a human analyst would otherwise have to produce manually.

The system is built as a modular monolith (see Section 16) using FastAPI + PostgreSQL, exposing a versioned REST API consumed by a React frontend. Every operational transaction (a stock movement, a purchase order, a shipment) both updates operational state **and** feeds a Kpi Engine and an AI Insight Engine that continuously re-evaluate the health of the business.

## 2. Business Problem

Mid-size and large businesses running physical goods operations typically suffer from:

- **Fragmented visibility**: inventory, purchasing, and sales data live in disconnected spreadsheets or siloed tools.
- **Reactive, not predictive, operations**: stockouts and overstock are discovered after they've already cost money.
- **No supplier accountability**: late deliveries and quality issues are not tracked or scored systematically.
- **No single source of truth for executives**: the CEO / Business Owner has no consolidated, real-time view of business health.
- **Manual reporting overhead**: hours spent building the same recurring Excel reports instead of acting on them.

SupplyIQ solves this by making every operational action observable, scoring the health of every entity (supplier, warehouse, product, category), and surfacing what needs attention **before** it becomes a crisis.

## 3. Product Vision

To be the operational nervous system for physical-goods businesses — combining transactional supply chain management with the analytical depth of a BI tool and the narrative clarity of an AI business analyst, so that any stakeholder, from a warehouse manager to a CEO, gets the right insight at the right altitude.

## 4. User Personas

| Persona | Role in System | Primary Goals | Key Screens |
|---|---|---|---|
| **Business Owner** | Admin | Understand overall business health, profitability, growth | Executive Dashboard, Business Health Score |
| **Executive / CEO** | Admin / Executive (read-heavy) | High-level KPIs, trends, AI-generated summaries | Executive Dashboard, Reports |
| **Operations Manager** | Manager | Cross-functional operational efficiency, bottlenecks | KPI Engine views, Alerts |
| **Supply Chain Manager** | Manager | End-to-end flow: procurement → inventory → shipment | Procurement, Logistics, Supplier Scorecards |
| **Warehouse Manager** | Manager / Employee | Stock accuracy, warehouse utilization, movements | Inventory Management, Warehouse Management |
| **Procurement Manager** | Manager | Supplier performance, reordering, purchase orders | Supplier Management, Purchase Orders |

## 5. Complete Feature List

**Operational**
- Multi-warehouse product & inventory management
- Category and supplier catalogs with many-to-many product-supplier mapping
- Purchase order lifecycle (draft → approved → sent → partially received → received → closed)
- Sales order lifecycle (draft → confirmed → fulfilled → shipped → delivered → cancelled)
- Inbound/outbound shipment tracking with carrier and status timeline
- Full inventory movement ledger (immutable, append-only)
- Customer directory with order history

**Intelligence & Analytics**
- KPI Engine computing 15+ supply chain metrics on schedule and on-demand
- AI Insight Engine generating natural-language business observations
- Executive dashboard with drill-down from company → warehouse → category → product
- Supplier reliability scoring
- Dead stock and stockout prediction
- Exportable reports (PDF/CSV/XLSX)

**Platform**
- JWT authentication with refresh tokens
- Role-Based Access Control (Admin / Manager / Employee) with a granular permission matrix
- Alerts & notification center (in-app, extensible to email/webhook)
- Full audit log of sensitive actions
- User & team management

## 6. Functional Requirements

- FR1: System shall support CRUD operations for Products, Categories, Suppliers, Warehouses, Customers.
- FR2: System shall maintain a real-time inventory quantity per (product, warehouse) pair, always reconciled against the movement ledger.
- FR3: System shall support creation and lifecycle transitions of Purchase Orders and Sales Orders with item-level line tracking.
- FR4: System shall record every inventory change as an InventoryMovement row; on-hand quantity is a derived/cached value, never edited directly.
- FR5: System shall compute and persist KPI snapshots on a scheduled basis (daily) and allow on-demand recomputation.
- FR6: System shall generate AI Insights by feeding aggregated KPI + entity data into an LLM-backed insight service, tagged by category and severity.
- FR7: System shall raise Alerts when thresholds are breached (e.g., stock below reorder point, warehouse over 85% capacity, supplier delayed 3+ times in 30 days).
- FR8: System shall enforce RBAC on every endpoint based on the Permissions Matrix (Section 25).
- FR9: System shall log all create/update/delete actions on sensitive entities to an Audit Log.
- FR10: System shall allow report export in CSV, XLSX, and PDF for any dashboard view or table.
- FR11: System shall support shipment tracking linked to either a Purchase Order (inbound) or Sales Order (outbound), with a status timeline.
- FR12: System shall expose a supplier scorecard aggregating on-time rate, quality flags, and lead-time variance.

## 7. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | API P95 latency < 300ms for CRUD; dashboard aggregate endpoints < 1.5s via cached KPI snapshots |
| Scalability | Backend stateless, horizontally scalable behind a load balancer; DB connection pooling via SQLAlchemy |
| Security | JWT with short-lived access tokens (15 min) + rotating refresh tokens; bcrypt/argon2 password hashing; parameterized queries only |
| Availability | Target 99.5% uptime; graceful degradation if AI Insight service is unavailable (core CRUD unaffected) |
| Data Integrity | Inventory on-hand values must always reconcile against the movement ledger; DB-level FK constraints + application-level transactional writes |
| Auditability | Every mutating action on financial/inventory entities is attributable to a user and timestamped |
| Extensibility | New KPI or AI insight types addable without schema migration (JSONB metadata columns) |
| Observability | Structured logging, request tracing IDs, health-check endpoint |
| Multi-tenancy readiness | Schema designed so an `organization_id` column can be added later without redesign |

## 8. Detailed Module Breakdown

1. **Authentication & Authorization** — JWT login/refresh/logout, password hashing, RBAC middleware, permission decorators per route.
2. **Product Management** — SKU, name, description, unit of measure, unit cost, unit price, category, reorder point, reorder quantity, active/discontinued status.
3. **Category Management** — hierarchical categories (self-referencing parent_id) for nested catalog structure.
4. **Supplier Management** — supplier profile, contact info, payment terms, lead time, linked products (many-to-many), reliability score (computed).
5. **Warehouse Management** — warehouse profile, address, capacity (units or volume), manager, utilization % (computed).
6. **Inventory Management** — per-warehouse stock levels, reorder alerts, safety stock, valuation (FIFO/weighted-average configurable).
7. **Inventory Movement Tracking** — immutable ledger of every IN/OUT/TRANSFER/ADJUSTMENT with reason and reference document.
8. **Purchase Order Management** — supplier-facing orders, line items, receiving workflow, partial receipt handling.
9. **Sales Order Management** — customer-facing orders, line items, fulfillment status, backorder handling.
10. **Shipment & Logistics Tracking** — carrier, tracking number, origin/destination warehouse or customer address, status timeline, ETA vs actual.
11. **Customer Management** — customer profile, order history, lifetime value (computed).
12. **Executive Dashboard** — role-aware, drill-down dashboard aggregating KPIs, alerts, and AI insights.
13. **KPI Engine** — scheduled + on-demand computation service producing versioned KPI snapshots (see Section 22).
14. **Alerts & Notifications** — rule engine evaluating thresholds; in-app notification feed per user.
15. **AI Insights Module** — LLM-backed service converting structured KPI/entity data into ranked, natural-language insights (see Section 23).
16. **Reports & Exports** — on-demand generation of CSV/XLSX/PDF from any tabular or dashboard view.
17. **Audit Logs** — append-only log of who did what, when, before/after state (JSONB diff).
18. **User Management** — invite users, assign roles, deactivate accounts, view activity.

## 9. User Workflow

**Typical daily flow (Warehouse Manager):**
Log in → view Inventory Management for assigned warehouse → see low-stock alerts → adjust stock via a physical count (creates an ADJUSTMENT movement) → receive an inbound shipment against a PO → system auto-generates an IN movement and updates on-hand quantity → dashboard KPIs recompute on schedule.

**Typical weekly flow (Procurement Manager):**
Log in → open Reorder Recommendations (AI Insight category) → review suggested products & quantities → create Purchase Orders per supplier → track PO status until received → review updated Supplier Reliability Score.

**Typical flow (Executive/CEO):**
Log in → Executive Dashboard loads Business Health Score, revenue/cost/profit trend, top AI insights of the day → drills into a flagged warehouse or category → exports a PDF summary for a board meeting.

## 10. Database Design

All primary keys are UUIDs. All tables include `created_at` and `updated_at` timestamps unless noted. Monetary values are stored as `NUMERIC(14,2)`. Quantities are stored as `NUMERIC(14,3)` to support fractional units (e.g., kilograms).

### 10.1 Entity List with Key Fields

**users**
`id, email (unique), password_hash, full_name, role_id (FK→roles), is_active, last_login_at`

**roles**
`id, name (Admin|Manager|Employee), description`

**permissions**
`id, code (e.g. "inventory:write"), description`

**role_permissions** (join table)
`role_id (FK), permission_id (FK)` — composite PK

**categories**
`id, name, parent_id (FK→categories, nullable, self-referencing)`

**products**
`id, sku (unique), name, description, category_id (FK→categories), unit_of_measure, unit_cost, unit_price, reorder_point, reorder_quantity, is_active`

**suppliers**
`id, name, contact_email, contact_phone, payment_terms, average_lead_time_days, reliability_score (cached, nullable), is_active`

**product_suppliers** (join table, many-to-many)
`id, product_id (FK), supplier_id (FK), supplier_sku, unit_cost, is_preferred` — unique on (product_id, supplier_id)

**warehouses**
`id, name, address, capacity_units, manager_id (FK→users, nullable)`

**inventory_items**
`id, product_id (FK), warehouse_id (FK), quantity_on_hand (cached/derived), quantity_reserved, safety_stock` — unique on (product_id, warehouse_id)

**inventory_movements**
`id, inventory_item_id (FK), movement_type (IN|OUT|TRANSFER|ADJUSTMENT), quantity, reference_type (PO|SO|SHIPMENT|MANUAL), reference_id (nullable UUID), reason, created_by (FK→users), created_at` *(append-only, no updated_at, no delete)*

**purchase_orders**
`id, supplier_id (FK), warehouse_id (FK, destination), status (draft|approved|sent|partially_received|received|closed|cancelled), order_date, expected_date, created_by (FK→users)`

**purchase_order_items**
`id, purchase_order_id (FK), product_id (FK), quantity_ordered, quantity_received, unit_cost`

**customers**
`id, name, email, phone, address, customer_type (retail|wholesale)`

**sales_orders**
`id, customer_id (FK), warehouse_id (FK, source), status (draft|confirmed|fulfilled|shipped|delivered|cancelled), order_date, created_by (FK→users)`

**sales_order_items**
`id, sales_order_id (FK), product_id (FK), quantity_ordered, quantity_fulfilled, unit_price`

**shipments**
`id, shipment_type (INBOUND|OUTBOUND), reference_type (PO|SO), reference_id, carrier, tracking_number, origin, destination, status (pending|in_transit|delivered|delayed|cancelled), expected_date, delivered_at`

**kpi_snapshots**
`id, kpi_code (e.g. "inventory_turnover"), scope_type (GLOBAL|WAREHOUSE|CATEGORY|SUPPLIER|PRODUCT), scope_id (nullable), value (NUMERIC), metadata (JSONB), snapshot_date`

**alerts**
`id, alert_type, severity (info|warning|critical), entity_type, entity_id, message, status (open|acknowledged|resolved), created_at, resolved_at`

**notifications**
`id, user_id (FK), alert_id (FK, nullable), title, body, is_read, created_at`

**ai_insights**
`id, category (inventory|supplier|warehouse|sales|financial), entity_type, entity_id (nullable), insight_text, confidence_score, severity, generated_at, model_version`

**reports**
`id, report_type, format (csv|xlsx|pdf), requested_by (FK→users), file_path, status (pending|ready|failed), created_at`

**audit_logs**
`id, user_id (FK), action, entity_type, entity_id, before_state (JSONB), after_state (JSONB), created_at`

### 10.2 Relationships & Cardinality

| Relationship | Cardinality |
|---|---|
| Role → User | 1 : N |
| Role ↔ Permission | M : N (via role_permissions) |
| Category → Category (parent) | 1 : N (self-referencing) |
| Category → Product | 1 : N |
| Product ↔ Supplier | M : N (via product_suppliers) |
| Warehouse → InventoryItem | 1 : N |
| Product → InventoryItem | 1 : N |
| InventoryItem → InventoryMovement | 1 : N |
| Supplier → PurchaseOrder | 1 : N |
| PurchaseOrder → PurchaseOrderItem | 1 : N |
| PurchaseOrderItem → Product | N : 1 |
| Customer → SalesOrder | 1 : N |
| SalesOrder → SalesOrderItem | 1 : N |
| SalesOrderItem → Product | N : 1 |
| PurchaseOrder / SalesOrder → Shipment | 1 : N (polymorphic via reference_type/reference_id) |
| User → AuditLog | 1 : N |
| User → Notification | 1 : N |
| Alert → Notification | 1 : N |

## 11. ER Diagram Description

Conceptually, the schema is organized into four clusters:

- **Identity Cluster**: `users ⇄ roles ⇄ permissions` — RBAC core.
- **Catalog Cluster**: `categories → products ⇄ suppliers` — what is sold/bought and from whom.
- **Operational Cluster**: `warehouses → inventory_items → inventory_movements`, and `purchase_orders/sales_orders → their line items → shipments` — the transactional heart of the system, all ultimately referencing `products` and `warehouses`.
- **Intelligence Cluster**: `kpi_snapshots`, `alerts`, `notifications`, `ai_insights`, `reports`, `audit_logs` — derived/observational tables that reference the operational cluster by `entity_type` + `entity_id` polymorphic pointers rather than hard foreign keys, keeping the intelligence layer decoupled and independently scalable/rebuildable.

The critical invariant: `inventory_items.quantity_on_hand` is **never written directly** by an API call — it is only ever updated as a side effect of an `inventory_movements` insert, inside the same DB transaction. This guarantees the ledger and the cached balance can never drift.

## 12. API Architecture

- **Style**: REST, JSON over HTTPS, versioned at `/api/v1`.
- **Auth**: `Authorization: Bearer <JWT>` on every route except `/auth/login` and `/auth/refresh`.
- **Pagination**: cursor-free offset pagination via `?page=&page_size=` on all list endpoints, returning `{items, total, page, page_size}`.
- **Filtering/Sorting**: query params per resource (e.g. `?category_id=&is_active=&sort=-created_at`).
- **Errors**: RFC7807-style problem responses `{"error": {"code": "...", "message": "...", "details": {...}}}` with consistent HTTP status codes (400/401/403/404/409/422/500).
- **Idempotency**: mutating financial endpoints (PO/SO status transitions) accept an `Idempotency-Key` header.
- **Async work**: report generation and AI insight batch generation run as background tasks (FastAPI `BackgroundTasks` initially, upgradeable to Celery/RQ) and are polled via a `status` field.

## 13. REST Endpoint List

**Auth**
`POST /api/v1/auth/login` · `POST /api/v1/auth/refresh` · `POST /api/v1/auth/logout` · `GET /api/v1/auth/me`

**Users & Roles**
`GET/POST /api/v1/users` · `GET/PATCH/DELETE /api/v1/users/{id}` · `GET /api/v1/roles` · `GET /api/v1/permissions`

**Categories**
`GET/POST /api/v1/categories` · `GET/PATCH/DELETE /api/v1/categories/{id}`

**Products**
`GET/POST /api/v1/products` · `GET/PATCH/DELETE /api/v1/products/{id}` · `GET /api/v1/products/{id}/suppliers`

**Suppliers**
`GET/POST /api/v1/suppliers` · `GET/PATCH/DELETE /api/v1/suppliers/{id}` · `GET /api/v1/suppliers/{id}/scorecard` · `GET /api/v1/suppliers/{id}/products`

**Warehouses**
`GET/POST /api/v1/warehouses` · `GET/PATCH/DELETE /api/v1/warehouses/{id}` · `GET /api/v1/warehouses/{id}/utilization`

**Inventory**
`GET /api/v1/inventory` (filter by warehouse/product) · `GET /api/v1/inventory/{id}` · `POST /api/v1/inventory/adjust` · `GET /api/v1/inventory/low-stock`

**Inventory Movements**
`GET /api/v1/inventory-movements` (filter by item/date/type) · `POST /api/v1/inventory-movements/transfer`

**Purchase Orders**
`GET/POST /api/v1/purchase-orders` · `GET/PATCH /api/v1/purchase-orders/{id}` · `POST /api/v1/purchase-orders/{id}/approve` · `POST /api/v1/purchase-orders/{id}/receive` · `POST /api/v1/purchase-orders/{id}/cancel`

**Sales Orders**
`GET/POST /api/v1/sales-orders` · `GET/PATCH /api/v1/sales-orders/{id}` · `POST /api/v1/sales-orders/{id}/confirm` · `POST /api/v1/sales-orders/{id}/fulfill` · `POST /api/v1/sales-orders/{id}/cancel`

**Shipments**
`GET/POST /api/v1/shipments` · `GET/PATCH /api/v1/shipments/{id}` · `POST /api/v1/shipments/{id}/status`

**Customers**
`GET/POST /api/v1/customers` · `GET/PATCH/DELETE /api/v1/customers/{id}` · `GET /api/v1/customers/{id}/orders`

**Dashboard & KPIs**
`GET /api/v1/dashboard/executive` · `GET /api/v1/kpis` · `GET /api/v1/kpis/{code}/history` · `POST /api/v1/kpis/recompute`

**Alerts & Notifications**
`GET /api/v1/alerts` · `PATCH /api/v1/alerts/{id}` · `GET /api/v1/notifications` · `PATCH /api/v1/notifications/{id}/read`

**AI Insights**
`GET /api/v1/ai-insights` (filter by category/entity) · `POST /api/v1/ai-insights/generate` · `GET /api/v1/ai-insights/dashboard-summary`

**Reports**
`POST /api/v1/reports` · `GET /api/v1/reports/{id}` · `GET /api/v1/reports/{id}/download`

**Audit Logs**
`GET /api/v1/audit-logs` (Admin only, filterable by user/entity/date)

Example response shape (Purchase Order):
```json
{
  "id": "uuid",
  "supplier": {"id": "uuid", "name": "Acme Components"},
  "warehouse": {"id": "uuid", "name": "East DC"},
  "status": "partially_received",
  "order_date": "2026-07-01",
  "expected_date": "2026-07-15",
  "items": [
    {"product_id": "uuid", "sku": "WID-100", "quantity_ordered": 500, "quantity_received": 300, "unit_cost": "4.25"}
  ],
  "total_value": "2125.00"
}
```

## 14. Backend Folder Structure

```
backend/
├── app/
│   ├── main.py                     # FastAPI app entrypoint
│   ├── core/
│   │   ├── config.py                # env/settings (Pydantic Settings)
│   │   ├── security.py              # JWT, password hashing
│   │   ├── permissions.py           # RBAC decorators/dependencies
│   │   └── logging.py
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy Base + session
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── user.py, role.py, permission.py
│   │   ├── product.py, category.py, supplier.py
│   │   ├── warehouse.py, inventory_item.py, inventory_movement.py
│   │   ├── purchase_order.py, sales_order.py, shipment.py
│   │   ├── customer.py
│   │   ├── kpi_snapshot.py, alert.py, notification.py
│   │   ├── ai_insight.py, report.py, audit_log.py
│   ├── schemas/                     # Pydantic request/response schemas (mirrors models/)
│   ├── api/
│   │   └── v1/
│   │       ├── router.py            # aggregates all routers
│   │       ├── auth.py, users.py, roles.py
│   │       ├── products.py, categories.py, suppliers.py
│   │       ├── warehouses.py, inventory.py, inventory_movements.py
│   │       ├── purchase_orders.py, sales_orders.py, shipments.py
│   │       ├── customers.py
│   │       ├── dashboard.py, kpis.py
│   │       ├── alerts.py, notifications.py
│   │       ├── ai_insights.py, reports.py, audit_logs.py
│   ├── services/                    # business logic, orchestrates repos + rules
│   │   ├── inventory_service.py
│   │   ├── purchase_order_service.py
│   │   ├── sales_order_service.py
│   │   ├── shipment_service.py
│   │   ├── kpi_engine/
│   │   │   ├── engine.py
│   │   │   └── calculators/         # one file per KPI (turnover.py, dead_stock.py, ...)
│   │   ├── ai_insight_engine/
│   │   │   ├── engine.py
│   │   │   ├── prompts.py
│   │   │   └── providers/anthropic_provider.py
│   │   ├── alert_rules_engine.py
│   │   └── report_service/
│   │       ├── generator.py
│   │       └── exporters/ (csv_exporter.py, xlsx_exporter.py, pdf_exporter.py)
│   ├── repositories/                # DB query layer, one per aggregate
│   ├── tasks/                       # background/scheduled jobs
│   │   ├── scheduler.py
│   │   ├── kpi_snapshot_job.py
│   │   └── ai_insight_job.py
│   └── utils/
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── alembic.ini
└── Dockerfile
```

## 15. Frontend Folder Structure

```
frontend/
├── src/
│   ├── main.tsx
│   ├── app/
│   │   ├── router.tsx                 # route definitions
│   │   └── providers.tsx              # auth/query/theme providers
│   ├── api/                           # typed API client, one file per resource
│   │   ├── client.ts                  # axios/fetch instance + interceptors
│   │   ├── products.ts, suppliers.ts, inventory.ts, purchaseOrders.ts,
│   │   │   salesOrders.ts, shipments.ts, dashboard.ts, aiInsights.ts, ...
│   ├── features/                      # feature-first organization
│   │   ├── auth/ (LoginPage, useAuth hook)
│   │   ├── dashboard/ (ExecutiveDashboard, KpiCard, InsightFeed)
│   │   ├── products/ (ProductList, ProductForm, ProductDetail)
│   │   ├── suppliers/ (SupplierList, SupplierScorecard)
│   │   ├── warehouses/ (WarehouseList, WarehouseUtilization)
│   │   ├── inventory/ (InventoryTable, StockAdjustModal, MovementLedger)
│   │   ├── purchase-orders/ (POList, POForm, POReceiveModal)
│   │   ├── sales-orders/ (SOList, SOForm)
│   │   ├── shipments/ (ShipmentTracker)
│   │   ├── customers/
│   │   ├── alerts/ (AlertCenter, NotificationBell)
│   │   ├── reports/ (ReportBuilder, ReportHistory)
│   │   └── admin/ (UserManagement, RolePermissions, AuditLogViewer)
│   ├── components/                    # shared/design-system components
│   │   ├── charts/ (RevenueTrendChart, KpiGauge, ...)
│   │   ├── layout/ (Sidebar, Topbar, DashboardShell)
│   │   └── ui/ (Button, Table, Modal, Badge, ...)
│   ├── hooks/                         # useDebounce, usePagination, usePermissions
│   ├── store/                         # global state (auth, notifications)
│   ├── types/                         # shared TS types mirroring backend schemas
│   └── utils/
├── public/
├── package.json
└── vite.config.ts
```

## 16. Microservice vs Monolith Discussion

**Recommendation: Modular Monolith at launch.**

| Factor | Monolith (chosen) | Microservices |
|---|---|---|
| Team size fit | Ideal for 1–6 engineers | Needs dedicated teams per service |
| Operational complexity | Single deploy, single DB, low ops overhead | Requires service mesh, distributed tracing, inter-service auth |
| Transactional integrity | Native DB transactions across modules (critical for inventory ↔ movement consistency) | Requires sagas/distributed transactions — much harder to keep correct |
| Iteration speed | Fast — one codebase, one CI pipeline | Slower initially due to infra investment |
| Future extraction path | Clean seams already exist (`services/` layer per module) → any module can be extracted later | N/A |

The codebase is structured with clear module boundaries (`services/`, `repositories/`, one router per domain) specifically so that high-load modules — most likely the **AI Insight Engine** and **KPI Engine** — can be extracted into standalone services later without a rewrite, once scale actually demands it. Premature microservices would slow this project down for no real benefit at current scale.

## 17. Authentication Flow

1. User submits credentials to `POST /auth/login`.
2. Backend verifies password hash, issues a short-lived **access token** (15 min, JWT, contains `user_id`, `role`) and a longer-lived **refresh token** (7 days, stored hashed in DB for revocation support).
3. Frontend stores the access token in memory and the refresh token in an httpOnly secure cookie.
4. Every API request attaches `Authorization: Bearer <access_token>`.
5. A FastAPI dependency (`get_current_user`) decodes and validates the token, loads the user + role + permissions, and injects them into the route.
6. A `require_permission("inventory:write")` dependency wraps sensitive routes and checks the loaded permission set, returning 403 if absent.
7. On access token expiry, frontend calls `POST /auth/refresh` using the cookie; backend rotates the refresh token and issues a new access token.
8. `POST /auth/logout` revokes the refresh token server-side.

## 18. Inventory Workflow

1. A stock-affecting event occurs: PO receipt, SO fulfillment, manual adjustment, or inter-warehouse transfer.
2. The relevant service (`inventory_service`) opens a DB transaction.
3. It inserts one or more `inventory_movements` rows describing the change (with `reference_type`/`reference_id` pointing back to the PO/SO/manual reason).
4. Within the same transaction, it updates `inventory_items.quantity_on_hand` by the movement delta.
5. If the resulting quantity crosses the product's `reorder_point`, the `alert_rules_engine` raises a `low_stock` alert and a notification is created for users with the relevant permission.
6. Transaction commits atomically — on-hand and ledger can never disagree.
7. The nightly `kpi_snapshot_job` recomputes turnover, dead stock, and aging metrics using the updated ledger.

## 19. Procurement Workflow

1. Procurement Manager creates a **draft** Purchase Order for a supplier, adding line items (product + quantity + unit cost) — often pre-populated from an AI reorder recommendation.
2. PO moves to **approved** (may require a manager/admin permission).
3. PO moves to **sent** once transmitted to the supplier (manual status update; email/EDI integration is a future enhancement).
4. As goods arrive, warehouse staff record receipt via `POST /purchase-orders/{id}/receive` with quantities per line — this triggers the Inventory Workflow (Section 18) to create IN movements.
5. PO auto-transitions to **partially_received** or **received** based on whether all lines are fully received.
6. On full receipt, the system updates the supplier's on-time/lead-time statistics feeding the **Supplier Reliability Score**.
7. PO can be **closed** (archived) or **cancelled** (only from draft/approved).

## 20. Shipment Workflow

**Outbound (Sales Order fulfillment):**
1. SO is confirmed → warehouse picks/packs → a `shipment` record is created with `shipment_type=OUTBOUND`, `reference_type=SO`.
2. Shipment status progresses: `pending → in_transit → delivered` (or `delayed`), each transition timestamped.
3. On `delivered`, linked SO line items are marked fulfilled; if all lines fulfilled, SO status becomes `delivered`.

**Inbound (Purchase Order):**
1. Supplier ships goods → a `shipment` record is created with `shipment_type=INBOUND`, `reference_type=PO`.
2. On `delivered`, warehouse staff perform the receiving step (Section 19, step 4).
3. If `expected_date` passes without `delivered` status, the alert engine flags the shipment as `delayed`, which also decrements the supplier's reliability score.

## 21. Dashboard Design

The **Executive Dashboard** is role-aware and drill-down capable:

- **Top strip**: Business Health Score, Supply Chain Efficiency Score, Revenue (MTD), Profit Margin — each with trend arrow vs. prior period.
- **AI Insight Feed**: ranked list of the day's top narrative insights (see Section 23), each linking to the relevant entity.
- **Alerts Panel**: open critical/warning alerts, sorted by severity and recency.
- **Operational Grid**: four cards — Inventory Health (turnover, dead stock %), Procurement (open POs, avg lead time), Warehouse Utilization (per-warehouse %), Fulfillment (order fulfillment rate, on-time delivery %).
- **Drill-down**: clicking any metric navigates to a filtered detail view (e.g., clicking "Warehouse East 91%" opens Warehouse Management pre-filtered).
- Role-based visibility: Employee-level users see only their assigned warehouse's operational data; Manager/Admin see cross-warehouse and financial data.

## 22. KPI Definitions

| KPI | Definition | Formula (conceptual) |
|---|---|---|
| Inventory Turnover | How many times inventory is sold/replaced in a period | COGS / Average Inventory Value |
| Dead Stock % | Share of inventory value with no movement in N days | Value of stagnant SKUs / Total Inventory Value |
| Stockout Prediction | Estimated days until a SKU hits zero at current sell-through | Current Qty / Avg Daily Outbound Rate |
| Supplier Reliability Score | Composite score of supplier dependability | Weighted(on-time rate, lead-time variance, quality flags) |
| Warehouse Utilization | How full a warehouse is | Units Stored / Capacity Units |
| Purchase Trends | Spend and volume trend by supplier/category over time | Rolling sum of PO value by period |
| Demand Trends | Sales velocity trend by product/category | Rolling sum of SO quantity by period |
| Monthly Growth | Revenue growth month-over-month | (Revenue_thisMonth − Revenue_lastMonth) / Revenue_lastMonth |
| Order Fulfillment Rate | % of order lines fulfilled without backorder | Fulfilled Line Qty / Ordered Line Qty |
| Lead Time Analysis | Actual vs promised supplier lead time | Actual Delivery Date − Order Date, vs. quoted lead time |
| Inventory Aging | Distribution of stock by age bucket | Age = Today − Last Received Date, bucketed |
| Revenue Analytics | Revenue by product/category/customer/time | Sum(SO line qty × unit_price) |
| Cost Analytics | COGS and procurement spend by dimension | Sum(PO line qty × unit_cost) |
| Profit Analysis | Margin by product/category | Revenue − COGS, and margin % |
| Business Health Score | Composite executive-level score | Weighted(revenue growth, margin, fulfillment rate, inventory health) |
| Supply Chain Efficiency Score | Composite operational score | Weighted(turnover, on-time delivery, warehouse utilization balance) |

All KPIs are stored as versioned `kpi_snapshots` rows so historical trend charts don't require recomputation from raw ledgers.

## 23. AI Insight Engine Design

**Principle**: the engine consumes **structured data** (KPI snapshots + entity records), never raw free text, and produces **grounded, cited natural-language insights** — it does not hallucinate metrics, it narrates metrics that were already computed deterministically by the KPI Engine.

**Pipeline:**
1. **Trigger**: scheduled job (daily) or on-demand `POST /ai-insights/generate`.
2. **Data assembly**: pull the latest `kpi_snapshots` for the requested scope, plus relevant entity context (e.g., supplier delivery history, warehouse capacity).
3. **Rule-based candidate detection**: a lightweight rules layer first flags candidate observations (e.g., "metric X crossed threshold Y") — this keeps the LLM from having to spot patterns in raw numbers, it only has to phrase pre-identified ones.
4. **LLM narration**: each candidate + its supporting numbers is passed to the LLM with a constrained prompt template ("Given this data, write one sentence describing the situation and, if relevant, a recommended action. Do not invent numbers not provided.") producing text like the examples in the source brief (e.g., an inventory runway warning, a supplier delay pattern, a warehouse capacity flag).
5. **Scoring & ranking**: each generated insight gets a `severity` and `confidence_score`; the feed is sorted by severity × recency.
6. **Persistence**: stored in `ai_insights` with `entity_type/entity_id` linkage so the frontend can deep-link from an insight to the underlying record.
7. **Fallback**: if the LLM provider is unavailable, the rule-based candidates are still surfaced as templated (non-LLM) insights so the dashboard degrades gracefully rather than breaking.

**Insight categories**: Inventory (runway/stockout, dead stock), Supplier (delay patterns, reliability drops), Warehouse (capacity), Sales (fulfillment time trend, category revenue concentration), Financial (margin shifts).

## 24. Recommended Charts

| Chart | Library | Use |
|---|---|---|
| Line chart | Recharts `LineChart` | Revenue/demand/purchase trends over time |
| Bar chart | Recharts `BarChart` | Category revenue contribution, warehouse utilization comparison |
| Stacked bar | Recharts `BarChart` (stacked) | Inventory aging buckets, order status breakdown |
| Gauge/Radial | Recharts `RadialBarChart` | Business Health Score, Supply Chain Efficiency Score, Warehouse Utilization % |
| Heatmap | Custom (D3 or Recharts grid) | Supplier reliability across suppliers × months |
| Sankey / Funnel | Recharts `Funnel` | Order fulfillment funnel (ordered → confirmed → shipped → delivered) |
| Sparkline | Recharts `LineChart` (minimal) | Inline KPI card trend indicators |
| Table with conditional formatting | Custom component | Low-stock list, open alerts list |

## 25. Permissions Matrix

Legend: **C**reate · **R**ead · **U**pdate · **D**elete · — none

| Module | Admin | Manager | Employee |
|---|---|---|---|
| Products | CRUD | CRUD | R |
| Categories | CRUD | CRUD | R |
| Suppliers | CRUD | CRUD | R |
| Warehouses | CRUD | RU | R |
| Inventory (view) | R | R | R (own warehouse) |
| Inventory (adjust) | CU | CU | CU (own warehouse, logged) |
| Purchase Orders | CRUD + approve | CRU + approve | R |
| Sales Orders | CRUD | CRU | CR (own warehouse) |
| Shipments | CRUD | CRU | RU (status updates) |
| Customers | CRUD | CRUD | R |
| Dashboard (financial) | R | R | — |
| Dashboard (operational) | R | R | R (own warehouse) |
| KPI Engine (trigger recompute) | C | — | — |
| Alerts | RU | RU | R (own warehouse) |
| AI Insights | R + trigger generate | R | R |
| Reports | CRUD | CR | R |
| User Management | CRUD | — | — |
| Audit Logs | R | — | — |

## 26. Development Roadmap

**M0 — Foundations (Week 1–2)**
Project scaffolding (backend + frontend), PostgreSQL on Neon, Alembic setup, base models for Identity Cluster (users, roles, permissions), JWT auth, RBAC middleware, CI pipeline skeleton.

**M1 — Catalog & Core Entities (Week 3–4)**
Categories, Products, Suppliers, Warehouses CRUD (API + basic frontend screens), product-supplier mapping.

**M2 — Inventory Core (Week 5–6)**
InventoryItem + InventoryMovement ledger, stock adjustment endpoint, transfer endpoint, on-hand reconciliation logic, low-stock detection.

**M3 — Procurement (Week 7–8)**
Purchase Orders + line items, approval/receive/cancel workflow, receiving triggers inventory movements, supplier lead-time tracking begins.

**M4 — Sales & Fulfillment (Week 9–10)**
Customers, Sales Orders + line items, confirm/fulfill/cancel workflow, fulfillment triggers OUT movements.

**M5 — Logistics (Week 11)**
Shipments (inbound + outbound), status timeline, linkage to PO/SO, delay detection.

**M6 — KPI Engine (Week 12–13)**
`kpi_snapshots` table, calculator modules for all 16 KPIs, scheduled daily job, on-demand recompute endpoint, KPI history endpoint.

**M7 — Alerts & Notifications (Week 14)**
Alert rules engine (low stock, warehouse capacity, supplier delay), notification feed, in-app bell UI.

**M8 — Executive Dashboard & Charts (Week 15–16)**
Dashboard aggregate endpoint, frontend dashboard shell, all chart components (Section 24), drill-down navigation, role-aware visibility.

**M9 — AI Insight Engine (Week 17–18)**
Rule-based candidate detection, LLM narration pipeline, `ai_insights` persistence, insight feed on dashboard, graceful degradation fallback.

**M10 — Reports, Audit Logs, Polish (Week 19–20)**
CSV/XLSX/PDF export service, audit logging on sensitive mutations, user management screens, permission matrix enforcement audit, performance pass (indexing, caching KPI queries), UAT and bug-fix cycle.

**M11 — Hardening & Launch (Week 21–22)**
Load testing, security review (JWT edge cases, RBAC bypass testing), deployment to Render, monitoring/alerting setup, documentation.

## 27. Future Enhancements

- Multi-tenancy (`organization_id` on all tables — schema already reserves this path)
- Demand forecasting with a proper time-series model (beyond rule-based stockout prediction)
- EDI/API integrations with real supplier systems and carrier tracking APIs (FedEx/UPS/DHL)
- Mobile app for warehouse staff (barcode scanning for movements/receiving)
- Automated PO generation from AI reorder recommendations (currently suggestion-only)
- Webhook/email delivery for alerts and notifications
- Multi-currency support for global suppliers/customers
- Advanced supplier risk scoring incorporating external signals (news, financial health)
- Configurable inventory valuation methods (FIFO/LIFO/weighted average) with GL integration
- Custom dashboard builder (drag-and-drop widgets per role)

## 28. Resume-Worthy Features

- Designed and implemented a **modular monolith** with clean service/repository seams enabling future microservice extraction.
- Built an **immutable ledger-based inventory system** guaranteeing on-hand/ledger consistency via transactional writes — a real-world pattern used in financial and logistics systems.
- Designed a **KPI computation engine** producing 16+ versioned, historically-queryable business metrics.
- Built an **LLM-backed AI Insight Engine** with a rules-first, LLM-narration-second architecture to keep generated insights grounded in real computed data rather than hallucinated.
- Implemented **granular RBAC** with a permission-matrix-driven authorization layer, not just role checks.
- Designed a **polymorphic intelligence layer** (alerts/insights/audit logs referencing entities generically) decoupled from the operational schema.
- Built a **role-aware, drill-down executive dashboard** comparable in structure to real enterprise BI tools.
- End-to-end ownership of **PRD → ERD → API design → roadmap** for a genuinely enterprise-scoped domain (supply chain), demonstrating product thinking beyond pure engineering.

---

*End of document. This specification is intended to be handed directly to an autonomous build agent (e.g., Antigravity) or a development team as the single source of truth for implementing SupplyIQ end-to-end.*
