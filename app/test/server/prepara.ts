// Preparazione comune alle prove delle rotte: uno schema pulito prima di ogni test.
//
// Applicare le migrazioni una volta sola e riusare il database renderebbe le prove
// dipendenti dall'ordine, che e' il modo piu' rapido di ottenere una suite che passa in
// locale e fallisce altrove. Qui lo schema si ricrea prima di ogni prova, e ogni prova
// scrive i propri dati.

import { applyD1Migrations, env } from "cloudflare:test";
import { beforeEach } from "vitest";

beforeEach(async () => {
  await env.DB.exec("DROP TABLE IF EXISTS gestori");
  await env.DB.exec("DROP TABLE IF EXISTS immobili");
  await env.DB.exec("DROP TABLE IF EXISTS membri");
  await env.DB.exec("DROP TABLE IF EXISTS organizzazioni");
  await env.DB.exec("DROP TABLE IF EXISTS d1_migrations");
  await applyD1Migrations(env.DB, env.MIGRAZIONI);
});
