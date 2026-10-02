import { Routes, Route } from "react-router-dom";

import PublicLayout from "../layouts/PublicLayout";
import AuthenticatedLayout from "../layouts/AuthenticatedLayout";

import Home from "../pages/Home";
import Features from "../pages/Features";
import HowItWorks from "../pages/HowItWorks";
import Download from "../pages/Download";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  // Authentication logic will be implemented in the functional phase.
  return children;
}

function NotFound() {
  return (
    <section>
      <h1>404 — Page Not Found</h1>
      <p>The requested page does not exist.</p>
    </section>
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicLayout><Home /></PublicLayout>} path="/" />

      <Route
        element={<PublicLayout><Features /></PublicLayout>}
        path="/features"
      />

      <Route
        element={<PublicLayout><HowItWorks /></PublicLayout>}
        path="/how-it-works"
      />

      <Route
        element={<PublicLayout><Download /></PublicLayout>}
        path="/download"
      />

      <Route
        element={<PublicLayout><Login /></PublicLayout>}
        path="/login"
      />

      <Route
        element={<PublicLayout><Register /></PublicLayout>}
        path="/register"
      />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <Dashboard />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="*"
        element={
          <PublicLayout>
            <NotFound />
          </PublicLayout>
        }
      />
    </Routes>
  );
}