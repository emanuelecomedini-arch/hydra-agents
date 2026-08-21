# HYDRA Agents — tre agenti AI che fanno girare il protocollo, gratis

Questo progetto prende l'idea di HYDRA Protocol e la fa funzionare davvero, con tre
agenti che lavorano in sequenza a ogni ciclo:

| Agente | File | Cosa fa |
|---|---|---|
| **Sentinella** | `agents/data_agent.py` | Raccoglie dati meteo pubblici e gratuiti (Open-Meteo, nessuna chiave richiesta) e li trasforma in una stima illustrativa dello stress idrico corrente per regione |
| **Orchestratore** | `agents/scheduler_agent.py` | Decide dove instradare ogni job flessibile. Gratis con una regola semplice, oppure vero agente AI (Claude) se aggiungi una chiave |
| **Cronista** | `agents/reporter_agent.py` | Scrive il log pubblico (`log.md`) e aggiorna `data.json`, il file che alimenta `dashboard_live.html` |

`orchestrate.py` li mette in fila. `dashboard_live.html` è la stessa dashboard che hai già visto, ma ora legge dati veri invece di numeri simulati in JavaScript.

## Apri subito la dashboard, senza installare nulla

Questo zip contiene già uno **snapshot di esempio** (`data.json`, `log.md`) generato e verificato da me. Apri `dashboard_live.html` con doppio click: la dashboard funziona subito e ti mostra un avviso giallo che ti ricorda che sono dati di esempio, non un ciclo reale.

## Il tuo primo ciclo vero (5 minuti, 2 comandi, nessun account richiesto)

```bash
pip install -r requirements.txt
python orchestrate.py
```

Questo sovrascrive `data.json` e `log.md` con un ciclo reale: dati meteo veri presi in questo momento (li ho testati io stesso contro la documentazione ufficiale di Open-Meteo prima di consegnarti il progetto), non più l'esempio. Ricarica `dashboard_live.html` nel browser e l'avviso giallo sparisce: da qui in poi stai vedendo il sistema vero.

A questo punto il sistema gira già in **modalità gratuita**: l'Orchestratore usa una regola semplice ("manda il job dove lo stress è più basso ora"), zero chiamate a un'API a pagamento, zero costo. Non ti serve nessun account per arrivare fin qui.

## Attivare il vero agente AI (facoltativo, pochi centesimi al mese)

1. Crea una chiave su [console.anthropic.com](https://console.anthropic.com).
2. Esportala come variabile d'ambiente prima di lanciare lo script:
   ```bash
   export ANTHROPIC_API_KEY="la-tua-chiave"
   python orchestrate.py
   ```
3. Da questo momento l'Orchestratore non applica più solo "il minimo stress": ragiona anche sulle finestre di flessibilità dei job per distribuire meglio il carico tra le regioni, e scrive una motivazione originale per ogni decisione invece del testo fisso della regola semplice.
4. Il modello di default è `claude-haiku-4-5-20251001`, scelto perché è il più economico adatto a un ciclo che gira più volte al giorno. Puoi cambiarlo impostando `HYDRA_MODEL` (ad esempio a `claude-sonnet-5` per un ragionamento più approfondito, a costo leggermente superiore).

Se la chiave manca, è scaduta o la rete non risponde, il sistema **non si blocca**: torna automaticamente alla modalità gratuita e lo scrive chiaramente nel log.

## Farlo girare da solo, gratis, per sempre (GitHub Actions)

Questa parte richiede necessariamente un tuo account: creare un repository o una chiave API sono azioni legate alla tua identità (email, autenticazione), quindi è l'unico pezzo che non posso completare al posto tuo. Ho ridotto i passaggi al minimo indispensabile:

1. Crea un repository pubblico su GitHub (trascina semplicemente tutti i file di questo zip nell'interfaccia web di GitHub quando crei il repository — non serve la riga di comando) e caricaci tutti i file di questo progetto (struttura invariata, incluse le cartelle `agents/` e `.github/`).
2. (Facoltativo) Se vuoi la modalità agente AI: vai su **Settings → Secrets and variables → Actions** del repository e aggiungi un secret chiamato `ANTHROPIC_API_KEY` con la tua chiave.
3. Vai sulla tab **Actions** del repository e attiva i workflow se richiesto.
4. Fatto: il workflow `run-agents.yml` esegue il ciclo ogni 6 ore in automatico, gratis (GitHub Actions non ha costi sui repository pubblici), e salva da solo `data.json` e `log.md` aggiornati nel repository.
5. Attiva **GitHub Pages** (Settings → Pages, sorgente: branch principale) per avere `dashboard_live.html` visibile online con un link pubblico, sempre aggiornato in automatico.

Da questo momento hai un sistema che si autoalimenta, gira da solo, e mostra a chiunque visiti il link una dashboard viva — senza che tu debba accendere un computer o pagare un server.

## Un limite da conoscere, onestamente

Lo stress idrico calcolato da questo sistema è una **stima illustrativa**: combina una categoria di stress di base per regione (scritta a mano in `regions.json`, ispirata nell'ordine di grandezza a indici pubblici) con le condizioni meteo del giorno. Non è un dato ufficiale né una misurazione reale di alcun data center — nessun operatore pubblica oggi quel dato in tempo reale. Il valore di questo progetto è dimostrare *come funzionerebbe* un protocollo del genere, e dare a te uno strumento reale, gratuito e modificabile per esplorarlo, non fornire un dato scientifico definitivo.

## Come estenderlo (idee, non obblighi)

- Aggiungi altre regioni in `regions.json` (basta lat/lon e uno stress di base).
- Aggiungi/modifica i job in `jobs.yaml` per riflettere carichi di lavoro reali che vuoi simulare.
- Sostituisci la fonte meteo o aggiungi una seconda fonte dati pubblica (es. indici di siccità regionali) in `data_agent.py`.
- Collega WATERMARK: usa le stesse fonti/metodologia per rendere coerenti i litri stimati mostrati nelle due pagine.
