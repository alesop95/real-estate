// Tipi delle variabili che il pool di prova mette a disposizione.
declare module "cloudflare:test" {
  interface ProvidedEnv {
    DB: D1Database;
    MODALITA: string;
    ACCESS_TEAM: string;
    ACCESS_AUD: string;
    MIGRAZIONI: D1Migration[];
  }
}
