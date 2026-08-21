# HYDRA Agents — registro

> Questo file si allunga automaticamente a ogni ciclo reale eseguito da orchestrate.py.
> Il primo blocco qui sotto è uno snapshot di esempio, non un ciclo reale.

## Esempio 2026-08-17T10:49:47+00:00 (dati di partenza, non un ciclo reale)

| Regione | Stress idrico | Job instradati |
|---|---|---|
| Virginia (US-EAST) | 73% | — |
| Dublino (EU-WEST) | 25% | training-llm-7b, finetune-vision-v3, batch-embed-nightly |
| Singapore (AP-SE) | 46% | — |
| São Paulo (SA-EAST) | 30% | — |
| Phoenix (US-SW) | 97% | — |

- **training-llm-7b** → `EU-WEST` — Regola semplice (modalità gratuita): Dublino ha lo stress idrico più basso attualmente (25%).
- **finetune-vision-v3** → `EU-WEST` — Regola semplice (modalità gratuita): Dublino ha lo stress idrico più basso attualmente (25%).
- **batch-embed-nightly** → `EU-WEST` — Regola semplice (modalità gratuita): Dublino ha lo stress idrico più basso attualmente (25%).
- **inference-api-live** → `locale` — Job non flessibile: eseguito nella regione di origine, non instradabile.

Litri stimati evitati (esempio): **86.4 L**
