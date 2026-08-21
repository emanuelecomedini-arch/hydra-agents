"""
Cronista — Agente di trasparenza e reportistica.

Trasforma le decisioni di scheduling in:
  - data.json  → il file che la dashboard live (dashboard_live.html) legge per mostrare
                 lo stato reale del sistema, non più dati simulati in JavaScript.
  - log.md     → un log leggibile in stile "registro pubblico", che si allunga a ogni ciclo.
  - state.json → un piccolo stato persistente (es. il totale cumulativo di litri stimati
                 evitati), così i numeri crescono nel tempo invece di ripartire da zero
                 a ogni esecuzione.
"""
import json
import os
from datetime import datetime, timezone

STATE_PATH = "state.json"
DATA_PATH = "data.json"
LOG_PATH = "log.md"


def _load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"liters_avoided_total": 0}


def _save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _estimate_liters_avoided(regions, decisions):
    """Stima grezza e dichiaratamente illustrativa dei litri "evitati" instradando verso
    la regione a minor stress invece che verso quella a maggior stress in quel ciclo.
    Coerente per ordine di grandezza con il calcolatore WATERMARK (decine di ml per job
    di tipo training/batch), non una misurazione reale di alcun data center."""
    worst = max(r["current_stress"] for r in regions)
    best = min(r["current_stress"] for r in regions)
    spread = max(0, worst - best)
    flexible_jobs = [d for d in decisions if d["region"] != "locale"]
    return round(spread * 0.4 * len(flexible_jobs), 2)


def write_report(regions, jobs, decisions):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state = _load_state()
    liters_this_run = _estimate_liters_avoided(regions, decisions)
    state["liters_avoided_total"] = round(state.get("liters_avoided_total", 0) + liters_this_run, 2)
    state["last_run"] = now
    _save_state(state)

    data = {
        "last_updated": now,
        "regions": [
            {
                "code": r["code"],
                "name": r["name"],
                "stress": r["current_stress"],
                "weather": r.get("weather", {}),
            }
            for r in regions
        ],
        "decisions": decisions,
        "liters_avoided_total": state["liters_avoided_total"],
        "liters_avoided_this_run": liters_this_run,
    }
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    lines = [f"\n## Ciclo {now}\n"]
    lines.append("| Regione | Stress idrico | Job instradati |")
    lines.append("|---|---|---|")
    for r in regions:
        jobs_here = [d["job"] for d in decisions if d["region"] == r["code"]]
        lines.append(f"| {r['name']} ({r['code']}) | {r['current_stress']}% | {', '.join(jobs_here) or '—'} |")
    lines.append("")
    for d in decisions:
        lines.append(f"- **{d['job']}** → `{d['region']}` — {d['rationale']}")
    lines.append(
        f"\nLitri stimati evitati in questo ciclo: **{liters_this_run} L** "
        f"(totale cumulativo dall'avvio: {state['liters_avoided_total']} L)\n"
    )

    mode = "a" if os.path.exists(LOG_PATH) else "w"
    with open(LOG_PATH, mode, encoding="utf-8") as f:
        f.write("\n".join(lines))

    return data
