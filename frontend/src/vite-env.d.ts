/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Set by Vercel at build time when deploying there. */
  readonly VERCEL?: string
  readonly VITE_API_BASE?: string
}
