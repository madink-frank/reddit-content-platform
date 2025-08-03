/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_WS_URL: string;
  readonly VITE_REDDIT_CLIENT_ID: string;
  readonly VITE_REDDIT_REDIRECT_URI: string;
  readonly VITE_NODE_ENV: string;
  readonly VITE_ENABLE_ANALYTICS: string;
  readonly VITE_ENABLE_NOTIFICATIONS: string;
  readonly VITE_ADMIN_USERNAMES: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}