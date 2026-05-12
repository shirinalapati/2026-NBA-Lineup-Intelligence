/// <reference types="vite/client" />

/** Injected by `vite.config.ts` `define` during production builds. */
declare const __API_ORIGIN__: string

interface ImportMetaEnv {
  readonly VITE_API_BASE?: string
}
