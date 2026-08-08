import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth';
import { DashboardShell } from '@/components/layout/DashboardShell';
import { LoginPage } from '@/features/auth/LoginPage';
import { ExecutiveDashboard } from '@/features/dashboard/ExecutiveDashboard';
import { ProductsPage } from '@/features/products/ProductsPage';
import { CategoriesPage } from '@/features/categories/CategoriesPage';
import { SuppliersPage } from '@/features/suppliers/SuppliersPage';
import { WarehousesPage } from '@/features/warehouses/WarehousesPage';
import { InventoryPage } from '@/features/inventory/InventoryPage';
import { PurchaseOrdersPage } from '@/features/purchase_orders/PurchaseOrdersPage';
import { SalesOrdersPage } from '@/features/sales_orders/SalesOrdersPage';
import { CustomersPage } from '@/features/customers/CustomersPage';
import { ShipmentsPage } from '@/features/shipments/ShipmentsPage';
import { AlertsPage } from '@/features/alerts/AlertsPage';
import { AiInsightsPage } from '@/features/ai_insights/AiInsightsPage';
import { ReportsPage } from '@/features/reports/ReportsPage';
import { UsersPage } from '@/features/users/UsersPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30, // 30 seconds
      retry: 1,
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardShell />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<ExecutiveDashboard />} />
            <Route path="products" element={<ProductsPage />} />
            <Route path="categories" element={<CategoriesPage />} />
            <Route path="suppliers" element={<SuppliersPage />} />
            <Route path="warehouses" element={<WarehousesPage />} />
            <Route path="inventory" element={<InventoryPage />} />
            <Route path="purchase-orders" element={<PurchaseOrdersPage />} />
            <Route path="sales-orders" element={<SalesOrdersPage />} />
            <Route path="customers" element={<CustomersPage />} />
            <Route path="shipments" element={<ShipmentsPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="ai-insights" element={<AiInsightsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="admin/users" element={<UsersPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
