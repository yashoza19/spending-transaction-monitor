import { createRootRoute, Outlet, useRouter } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import { DashboardHeader } from '../components/dashboard-header/dashboard-header';
import { Footer } from '../components/footer/footer';
import { DevModeBanner } from '../components/dev-mode/DevModeBanner';
import { useAuth } from '../hooks/useAuth';

function RootComponent() {
  const router = useRouter();
  const auth = useAuth();

  // Debug logging
  console.log('RootComponent auth state:', {
    isAuthenticated: auth.isAuthenticated,
    isLoading: auth.isLoading,
    user: auth.user,
    pathname: router.state.location.pathname
  });

  // Hide header and banner on login page or when user is not authenticated
  const shouldShowHeader =
    router.state.location.pathname !== '/login' &&
    auth.isAuthenticated;

  console.log('RootComponent shouldShowHeader:', shouldShowHeader);

  // For login page, render full page without any layout
  if (router.state.location.pathname === '/login') {
    return (
      <div className="min-h-screen">
        <Outlet />
        <TanStackRouterDevtools />
      </div>
    );
  }

  // Show loading state while auth is initializing
  // But only if we're not authenticated yet
  if (auth.isLoading && !auth.isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div>Loading...</div>
        <TanStackRouterDevtools />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Development Mode Banner - show when authenticated and not on login page */}
      {shouldShowHeader && <DevModeBanner />}

      {/* Dashboard Header - show when authenticated and not on login page */}
      {shouldShowHeader && <DashboardHeader />}

      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      <TanStackRouterDevtools />
    </div>
  );
}

export const Route = createRootRoute({
  component: RootComponent,
});
