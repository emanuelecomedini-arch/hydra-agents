"""
Orchestratore — Agente di scheduling water-aware.

Due modalità, per garantire che il progetto funzioni a costo zero assoluto e diventi
un vero agente AI solo quando lo decidi tu:

  - MODALITÀ GRATUITA (default, nessuna chiave richiesta): applica una regola semplice,
    instrada ogni job flessibile verso la regione con lo stress idrico più basso in quel
    momento. Zero chiamate API, zero costo, funziona sempre.

  - MODALITÀ AGENTE AI (opzionale): se imposti la variabile d'ambiente ANTHROPIC_API_KEY,
    un vero agente Claude ragiona sulla decisione considerando non solo lo stress minimo,
    ma anche le finestre di flessibilità dei job, per bilanciare meglio il carico tra le
    regioni invece di concentrarlo sempre su una sola. Costo: frazioni di centesimo per
    ciclo con un modello economico come Haiku.
"""
import os
import json

MODEL = os.environ.get("HYDRA_MODEL", "claude-haiku-4-5-20251001")


def _best_region_simple(regions):
    return min(regions, key=lambda r: r["current_stress"])


def decide_rule_based(regions, jobs):
    best = _best_region_simple(regions)
    decisions = []
    for job in jobs:
        if job.get("flexible"):
            decisions.append({
                "job": job["name"],
                "region": best["code"],
                "rationale": (
                    f"Regola semplice (modalità gratuita): {best['name']} ha lo stress "
                    f"idrico più basso attualmente ({best['current_stress']}%)."
                ),
            })
        else:
            decisions.append({
                "job": job["name"],
                "region": "locale",
                "rationale": "Job non flessibile: eseguito nella regione di origine, non instradabile.",
            })
    return decisions


def decide_with_agent(regions, jobs):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return decide_rule_based(regions, jobs)

    try:
        import anthropic
    except ImportError:
        return decide_rule_based(regions, jobs)

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = (
        "Sei l'agente di scheduling del protocollo HYDRA, un sistema che instrada carichi "
        "di calcolo AI verso le regioni con minore stress idrico stimato. Ricevi un elenco "
        "di regioni con il loro stress idrico corrente (0-100, più alto è peggio) e un "
        "elenco di job. Per ogni job flessibile, scegli la regione più adatta bilanciando "
        "lo stress idrico corrente con la finestra di flessibilità dichiarata: i job con "
        "finestra più ampia possono tollerare una regione leggermente meno ottimale se "
        "questo aiuta a distribuire il carico invece di concentrarlo tutto sulla stessa "
        "regione. I job non flessibili restano sempre nella regione locale, valore "
        "\"locale\". Rispondi ESCLUSIVAMENTE con un array JSON valido, nessun testo prima "
        "o dopo, nel formato: "
        '[{"job": "...", "region": "CODICE o locale", "rationale": "una frase breve in italiano"}]'
    )

    user_payload = {
        "regions": [
            {"code": r["code"], "name": r["name"], "current_stress": r["current_stress"]}
            for r in regions
        ],
        "jobs": jobs,
    }

    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}],
        )
        text = "".join(block.text for block in msg.content if block.type == "text").strip()
        for fence in ("```json", "```"):
            if text.startswith(fence):
                text = text[len(fence):]
            if text.endswith("```"):
                text = text[:-3]
        decisions = json.loads(text.strip())
        return decisions
    except Exception as e:
        # In caso di qualunque problema (rete, parsing, quota esaurita), non blocchiamo
        # il sistema: torniamo alla modalità gratuita a regola semplice e lo segnaliamo.
        fallback = decide_rule_based(regions, jobs)
        for d in fallback:
            d["rationale"] += f" [fallback: agente AI non disponibile — {e}]"
        return fallback


def decide(regions, jobs):
    return decide_with_agent(regions, jobs)
