/**
 * Authentication configuration
 * Handles both development bypass and production OIDC setup
 * Uses runtime environment configuration from window.ENV
 */

export interface AuthConfig {
  bypassAuth: boolean;
  environment: 'development' | 'production' | 'staging' | 'test';
  keycloak: {
    authority: string;
    clientId: string;
    redirectUri: string;
    postLogoutRedirectUri: string;
  };
}

/**
 * Get runtime environment configuration
 * Falls back to import.meta.env for development mode (vite dev server)
 */
function getRuntimeConfig() {
  // In production (served by nginx/serve), window.ENV is injected
  if (typeof window !== 'undefined' && window.ENV) {
    return {
      bypassAuth: window.ENV.BYPASS_AUTH === true,
      environment: window.ENV.ENVIRONMENT as AuthConfig['environment'],
      keycloakUrl: window.ENV.KEYCLOAK_URL,
      keycloakClientId: window.ENV.KEYCLOAK_CLIENT_ID,
    };
  }

  // Fallback to build-time env vars for local development (vite dev)
  return {
    bypassAuth: import.meta.env.VITE_BYPASS_AUTH === 'true',
    environment: (import.meta.env.VITE_ENVIRONMENT ||
      'development') as AuthConfig['environment'],
    keycloakUrl:
      import.meta.env.VITE_KEYCLOAK_URL ||
      'http://localhost:8080/realms/spending-monitor',
    keycloakClientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || 'spending-monitor',
  };
}

const runtimeConfig = getRuntimeConfig();

export const authConfig: AuthConfig = {
  environment: runtimeConfig.environment,
  bypassAuth: runtimeConfig.bypassAuth,
  keycloak: {
    authority: runtimeConfig.keycloakUrl,
    clientId: runtimeConfig.keycloakClientId,
    redirectUri:
      typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000',
    postLogoutRedirectUri:
      typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000',
  },
};

// Log configuration in development
if (import.meta.env.DEV || runtimeConfig.environment === 'development') {
  console.log('🔧 Auth configuration loaded:', {
    bypassAuth: authConfig.bypassAuth,
    environment: authConfig.environment,
    source: window.ENV ? 'runtime (window.ENV)' : 'build-time (import.meta.env)',
  });
}
