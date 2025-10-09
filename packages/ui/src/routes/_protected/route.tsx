import { createFileRoute, Outlet, useNavigate } from '@tanstack/react-router';
import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { DashboardHeader } from '../../components/dashboard-header/dashboard-header';
import { DevModeBanner } from '../../components/dev-mode/DevModeBanner';
import { Footer } from '../../components/footer/footer';
import { Card } from '../../components/atoms/card/card';

export const Route = createFileRoute('/_protected')({
  component: ProtectedPages,
});

function ProtectedPages() {
  const auth = useAuth();
  const navigate = useNavigate();

  // Handle authentication redirect
  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      const currentPath = window.location.pathname + window.location.search;
      navigate({
        to: '/login',
        search: { redirect: currentPath, error: '' },
      });
    }
  }, [auth.isAuthenticated, auth.isLoading, navigate]);

  // Show loading state while checking auth
  if (auth.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30">
        <Card className="max-w-md w-full p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Checking authentication...</p>
        </Card>
      </div>
    );
  }

  // Show error state if auth failed
  if (auth.error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30">
        <Card className="max-w-md w-full p-8 text-center space-y-4">
          <h2 className="text-xl font-semibold text-destructive">
            Authentication Error
          </h2>
          <p className="text-muted-foreground">
            {auth.error.message || 'Unable to verify authentication status'}
          </p>
        </Card>
      </div>
    );
  }

  // Don't render until auth is confirmed
  if (!auth.isAuthenticated || !auth.user) {
    return null;
  }

  // All checks passed - render protected content
  return (
    <div className="min-h-screen flex flex-col">
      {/* Development Mode Banner */}
      <DevModeBanner />

      {/* Dashboard Header */}
      <DashboardHeader />

      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
}
