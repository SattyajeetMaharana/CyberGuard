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

import Threats from "../pages/Threats";
import Incidents from "../pages/Incidents";
import CyberScore from "../pages/CyberScore";
import Departments from "../pages/Departments";
import Employees from "../pages/Employees";
import Devices from "../pages/Devices";
import Policies from "../pages/Policies";
import Settings from "../pages/Settings";
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  // Authentication logic will be implemented in the functional phase.
  return children;
}

function NotFound() {
  return (
    <section className="not-found-page">
      <span className="organization-placeholder-label">
        CyberGuard
      </span>

      <h1>404 — Page Not Found</h1>

      <p>The requested page does not exist.</p>
    </section>
  );
}

export default function AppRoutes() {
  return (
    <Routes>
      {/* ================================
          Public Routes
          ================================ */}

      <Route
        path="/"
        element={
          <PublicLayout>
            <Home />
          </PublicLayout>
        }
      />

      <Route
        path="/features"
        element={
          <PublicLayout>
            <Features />
          </PublicLayout>
        }
      />

      <Route
        path="/how-it-works"
        element={
          <PublicLayout>
            <HowItWorks />
          </PublicLayout>
        }
      />

      <Route
        path="/download"
        element={
          <PublicLayout>
            <Download />
          </PublicLayout>
        }
      />

      <Route
        path="/login"
        element={
          <PublicLayout>
            <Login />
          </PublicLayout>
        }
      />

      <Route
        path="/register"
        element={
          <PublicLayout>
            <Register />
          </PublicLayout>
        }
      />

      {/* ================================
          Organization Routes
          ================================ */}

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
        path="/threats"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <Threats />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />

      <Route
          path="/incidents"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <Incidents />
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />

      <Route
        path="/cyber-score"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <CyberScore />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />


      <Route
        path="/departments"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <Departments />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/employees"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <Employees />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/devices"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <Devices />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/policies"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <Policies />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <AuthenticatedLayout>
              <Settings />
            </AuthenticatedLayout>
          </ProtectedRoute>
        }
      />

      {/* ================================
          404
          ================================ */}

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