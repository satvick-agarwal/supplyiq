# ⚡ SupplyIQ — Enterprise Supply Chain Intelligence Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Cloud-4169E1?style=flat&logo=postgresql&logoColor=white)](https://neon.tech)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SupplyIQ** is a modular enterprise Supply Chain Intelligence Platform that integrates procurement, multi-warehouse inventory, logistics, supplier scorecards, and executive business analytics into a single operational system.

Rather than acting as a standard CRUD tracker, SupplyIQ operates as a **decision intelligence layer**: every inventory movement, purchase order, and shipment automatically feeds an asynchronous **KPI Engine** (computing 16+ live business metrics) and an **AI Insight Engine** (synthesizing narrative operational signals).

---

## 🌟 Key Features

### 📦 Core Operations
- **Multi-Warehouse Inventory**: Real-time stock levels, reservations, and safety thresholds across geographically distributed facilities.
- **Immutable Movement Ledger**: Append-only transactional audit trail for stock movements (`IN`, `OUT`, `TRANSFER`, `ADJUSTMENT`) to maintain data integrity.
- **Purchase Order (PO) Lifecycle**: State machine (`draft` → `approved` → `sent` → `partially_received` → `received` → `closed`) with partial delivery receipt tracking.
- **Sales Order (SO) Lifecycle**: Order fulfillment pipeline (`draft` → `confirmed` → `fulfilled` → `shipped` → `delivered` → `cancelled`).
- **Shipment Logistics**: Inbound & outbound carrier tracking, waybill/tracking numbers, and transit status timelines.
- **Supplier & Customer Directories**: Detailed partner profiles with payment terms, lead times, and transaction histories.

### 🧠 Intelligence & Analytics
- **Live KPI Engine**: Computes 16+ derived metrics on-demand and on schedule (Inventory Turnover, Dead Stock %, Order Fulfillment Rate, Gross Margin, On-Time Delivery Rate, Business Health Score).
- **AI Insight Engine**: Rule-based observation detector paired with natural-language narrative synthesis (identifies stockout risks, supplier delays, and dead stock anomalies).
- **Executive BI Dashboard**: Interactive graphs (via Recharts) with company-wide and entity-level drilldowns.
- **Supplier Reliability Scorecard**: Empirical scoring based on historical delivery timelines, quality compliance, and fulfillment accuracy.

### 🛡️ Platform & Security
- **Role-Based Access Control (RBAC)**: Fine-grained permissions matrix across Admin, Manager, and Employee roles.
- **JWT Authentication**: Short-lived access tokens (15m) with automatic silent rotation via refresh tokens.
- **Full Audit Logging**: Automated before/after JSON change capture for sensitive state transitions.
- **Real-Time Notification Hub**: Critical alerts and threshold violation notifications.

---

## 🏗️ Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────┐
│                   React 19 + Vite                      │
│      TypeScript · Tailwind CSS · Zustand · Recharts     │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON / Bearer JWT)
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Modular Monolith              │
│       Pydantic v2 · SQLAlchemy 2.0 (Async) · Alembic   │
├───────────────────────────┬────────────────────────────┤
│       KPI Engine          │      AI Insight Engine     │
└───────────────────────────┼────────────────────────────┘
                            │ asyncpg / psycopg2
┌───────────────────────────▼────────────────────────────┐
│            PostgreSQL (Neon Serverless Cloud)          │
│       15 Relational Tables · UUID Primary Keys · JSONB │
└────────────────────────────────────────────────────────┘
```

- **Backend**: Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async Engine), [Alembic](https://alembic.sqlalchemy.org/), [Pydantic v2](https://docs.pydantic.dev/).
- **Database**: PostgreSQL (hosted on [Neon](https://neon.tech/)), connection pooling, async I/O via `asyncpg`.
- **Frontend**: [React 19](https://react.dev/), [Vite](https://vitejs.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS v4](https://tailwindcss.com/), [Zustand](https://github.com/pmndrs/zustand) (state), [TanStack Query](https://tanstack.com/query) (caching), [Lucide Icons](https://lucide.dev/).

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** & **npm** installed
- A **PostgreSQL** database (e.g., Neon serverless)

---

### 1. Backend Setup

1. Open your terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment variables:
   Copy `.env.example` to `.env` and configure your database credentials:
   ```bash
   cp .env.example .env
   ```
   Ensure your `DATABASE_URL` is configured:
   ```env
   DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require
   SECRET_KEY=your-32-character-secret-key-goes-here
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Seed demo data (idempotent, skips if data already exists):
   ```bash
   python -m app.db.seed
   ```

7. Start the backend development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   * Backend API: `http://localhost:8000`
   * Interactive Swagger Documentation: `http://localhost:8000/docs`
   * ReDoc: `http://localhost:8000/redoc`

---

### 2. Frontend Setup

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   * Frontend Application: `http://localhost:5173`

---

## 👥 Seed Demo Accounts

The database comes pre-loaded with realistic demo data across multiple personas:

| Persona | Role | Email | Password |
|---|---|---|---|
| **Alex Administrator** | Admin (Full Access) | `admin@supplyiq.com` | `Admin@123` |
| **Marcus Manager** | Operations Manager | `manager@supplyiq.com` | `Manager@123` |
| **Sarah Supply Chain** | Supply Chain Manager | `scm@supplyiq.com` | `Manager@123` |
| **Will Warehouse** | Warehouse Operator | `warehouse@supplyiq.com` | `Emp@12345` |
| **Olivia Ops** | Operations Employee | `ops@supplyiq.com` | `Emp@12345` |

*(The login screen also provides quick preset buttons for 1-click credential auto-fill).*

---

## 🔌 API Endpoints Overview

| Module | Route Prefix | Key Endpoints | Description |
|---|---|---|---|
| **Auth** | `/api/v1/auth` | `POST /login`, `POST /refresh`, `GET /me` | Authentication & token rotation |
| **Dashboard** | `/api/v1/dashboard` | `GET /executive`, `GET /operational` | Aggregated executive KPIs & alerts |
| **Inventory** | `/api/v1/inventory` | `GET /`, `POST /adjust`, `POST /transfer` | Stock balances & warehouse adjustments |
| **Movements** | `/api/v1/inventory/movements` | `GET /` | Immutable movement ledger |
| **Procurement** | `/api/v1/purchase-orders` | `GET /`, `POST /`, `POST /{id}/receive` | PO lifecycle & line receipts |
| **Sales** | `/api/v1/sales-orders` | `GET /`, `POST /`, `POST /{id}/fulfill` | Sales orders & fulfillment status |
| **Logistics** | `/api/v1/shipments` | `GET /`, `POST /`, `PATCH /{id}/status` | Inbound / outbound freight tracking |
| **KPIs** | `/api/v1/kpis` | `GET /latest`, `GET /{code}/history`, `POST /recompute` | Time-series supply chain metrics |
| **AI Insights** | `/api/v1/ai-insights` | `GET /`, `GET /dashboard-summary`, `POST /generate` | Narrative insights & recommendations |
| **Catalogs** | `/api/v1/products`, `/suppliers`, `/warehouses`, `/customers` | Full CRUD | Master entity management |

---

## 📁 Repository Structure

```
SupplyIQ/
├── SupplyIQ_Product_Design_Document.md # Exhaustive Product Design & Architecture Specification
├── backend/
│   ├── alembic/                       # Database migration configurations & versions
│   │   ├── versions/                  # Schema revision scripts
│   │   └── env.py                     # Alembic sync runner with psycopg2
│   ├── app/
│   │   ├── api/v1/                    # Versioned REST controllers & routes
│   │   ├── core/                      # Settings, security, JWT, and permissions matrix
│   │   ├── db/                        # Base models, engine sessions, and seed script
│   │   ├── models/                    # SQLAlchemy 2.0 ORM domain models
│   │   ├── repositories/              # Database data access abstraction layer
│   │   ├── schemas/                   # Pydantic v2 validation schemas
│   │   └── services/                  # Business logic (KPI engine, AI insights, PO/SO)
│   ├── requirements.txt               # Python package dependencies
│   └── alembic.ini                    # Alembic migration tooling config
└── frontend/
    ├── src/
    │   ├── api/                       # Axios client & typed API service endpoints
    │   ├── components/                # Reusable UI primitives & layout shells
    │   ├── features/                  # Domain page modules (Dashboard, Inventory, PO, etc.)
    │   ├── store/                     # Zustand state management (Auth, UI)
    │   ├── types/                     # Shared TypeScript interfaces
    │   ├── index.css                  # Design system tokens & animations
    │   └── App.tsx                    # React router & protected routes
    ├── package.json                   # NPM dependencies & scripts
    └── vite.config.ts                 # Vite bundler & reverse proxy configuration
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
