# -*- coding: utf-8 -*-
"""Cliente per il modello linguistico locale servito da Ollama.

L'uso previsto è la strutturazione del testo di un annuncio incollato a mano:
il contenuto resta sulla rete locale e non raggiunge alcun servizio esterno, il
che è la ragione principale per cui questa strada è preferita a un servizio in
cloud. La dipendenza è opzionale: se l'host non risponde il resto del programma
continua a funzionare e l'inserimento torna manuale.

L'endpoint predefinito è quello standard di Ollama in locale. Chi serve il modello
da un'altra macchina della propria rete imposta la variabile d'ambiente OLLAMA_HOST,
che ha la precedenza: l'indirizzo di una rete privata non ha ragione di stare nel
codice sorgente di una repository pubblica.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

HOST_PREDEFINITO = "http://localhost:11434"
MODELLO_PREDEFINITO = "qwen3:14b"
MODELLO_EMBEDDING = "bge-m3:latest"
TIMEOUT_SECONDI = 300


class LlmNonDisponibile(RuntimeError):
    """L'host Ollama non risponde o il modello richiesto non è installato."""


class ClienteLocale:
    """Cliente minimale per le due sole chiamate che servono qui."""

    def __init__(self, host: str = "", modello: str = MODELLO_PREDEFINITO) -> None:
        self.host = (host or os.environ.get("OLLAMA_HOST") or HOST_PREDEFINITO).rstrip("/")
        self.modello = modello

    def _chiama(self, percorso: str, corpo: dict) -> dict:
        richiesta = urllib.request.Request(
            f"{self.host}{percorso}",
            data=json.dumps(corpo).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(richiesta, timeout=TIMEOUT_SECONDI) as risposta:
                return json.loads(risposta.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise LlmNonDisponibile(f"{self.host} non raggiungibile: {e.reason}") from e

    def modelli(self) -> list[str]:
        """Elenca i modelli installati sull'host."""
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=15) as risposta:
                dati = json.loads(risposta.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise LlmNonDisponibile(f"{self.host} non raggiungibile: {e.reason}") from e
        return [m["name"] for m in dati.get("models", [])]

    def disponibile(self) -> bool:
        try:
            return self.modello in self.modelli()
        except LlmNonDisponibile:
            return False

    def completa(self, prompt: str, formato_json: bool = False, temperatura: float = 0.0) -> str:
        """Genera una risposta. Con `formato_json` vincola l'uscita a JSON valido."""
        corpo = {
            "model": self.modello,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"temperature": temperatura},
        }
        if formato_json:
            corpo["format"] = "json"
        dati = self._chiama("/api/generate", corpo)
        return dati.get("response", "")

    def vettore(self, testo: str, modello: str = MODELLO_EMBEDDING) -> list[float]:
        """Embedding di un testo, usato per riconoscere annunci duplicati.

        Lo stesso immobile ricompare spesso su portali diversi con testo riscritto e
        prezzo leggermente diverso: il confronto sul solo link non lo intercetta, il
        confronto semantico si'.
        """
        dati = self._chiama("/api/embed", {"model": modello, "input": testo})
        vettori = dati.get("embeddings") or []
        return vettori[0] if vettori else []


def somiglianza(a: list[float], b: list[float]) -> float:
    """Coseno fra due vettori, zero se uno dei due è vuoto."""
    if not a or not b or len(a) != len(b):
        return 0.0
    prodotto = sum(x * y for x, y in zip(a, b))
    norma_a = sum(x * x for x in a) ** 0.5
    norma_b = sum(y * y for y in b) ** 0.5
    if norma_a == 0 or norma_b == 0:
        return 0.0
    return prodotto / (norma_a * norma_b)
