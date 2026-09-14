// Il foglio di stile importato da un modulo TypeScript.
//
// Serve perche' `import "./stile.css"` non e' un'importazione di codice: e' un'istruzione per
// chi costruisce, che raccoglie il foglio e lo mette nella pagina. Al compilatore quel file
// non risulta un modulo, e senza questa dichiarazione rifiuta la riga. Si dichiara qui invece
// di aggiungere i tipi completi di Vite fra quelli globali, perche' quelli portano con se'
// anche l'ambiente di `import.meta`, che in questo progetto convive con i tipi dei Worker e
// non conviene mescolare.

declare module "*.css";
