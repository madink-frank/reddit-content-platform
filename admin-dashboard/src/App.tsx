
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './contexts/NotificationContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import Layout from './components/layout/Layout';
import { withLazyLoading } from './utils/lazyLoad';

// Lazy load pages for better performance
const LoginPage = withLazyLoading(() => import('./pages/LoginPage'));
const DashboardPage = withLazyLoading(() => import('./pages/DashboardPage'));
const KeywordsPage = withLazyLoading(() => import('./pages/KeywordsPage'));
const CrawlingPage = withLazyLoading(() => import('./pages/CrawlingPage'));
const PostsPage = withLazyLoading(() => import('./pages/PostsPage'));
const AnalyticsPage = withLazyLoading(() => import('./pages/AnalyticsPage'));
const ContentPage = withLazyLoading(() => import('./pages/ContentPage'));
const SystemMonitoringPage = withLazyLoading(() => import('./pages/SystemMonitoringPage'));
const SettingsPage = withLazyLoading(() => import('./pages/SettingsPage'));

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NotificationProvider>
          <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/auth/callback" element={<LoginPage />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route
                          path="/"
                          element={<Navigate to="/dashboard" replace />}
                        />
                        <Route path="/dashboard" element={<DashboardPage />} />
                        <Route path="/keywords" element={<KeywordsPage />} />
                        <Route path="/crawling" element={<CrawlingPage />} />
                        <Route path="/posts" element={<PostsPage />} />
                        <Route path="/analytics" element={<AnalyticsPage />} />
                        <Route path="/content" element={<ContentPage />} />
                        <Route path="/monitoring" element={<SystemMonitoringPage />} />
                        <Route path="/settings" element={<SettingsPage />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </div>
        </NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
