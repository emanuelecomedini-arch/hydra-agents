"""
Punto di ingresso del sistema di agenti HYDRA.

Esegue il ciclo completo: raccolta dati (Sentinella) -> decisione di scheduling
(Orchestratore) -> report e aggiornamento dashboard (Cronista).

Pensato per girare gratis:
  - in locale, lanciando `python orchestrate.py` quando vuoi;
  - automaticamente e gratis su GitHub Actions (vedi .github/workflows/run-agents.yml),
    senza bisogno di un server sempre acceso o di pagare hosting.
"""
import json
import yaml

from agents.data_agent import collect
from agents.scheduler_agent import decide
from agents.reporter_agent import write_report


def main():
    with open("regions.json", "r", encoding="utf-8") as f:
        regions_static = json.load(f)
    with open("jobs.yaml", "r", encoding="utf-8") as f:
        jobs = yaml.safe_load(f)

    print("Sentinella: raccolgo i segnali meteo/stress per ogni regione...")
    regions = collect(regions_static)

    print("Orchestratore: decido dove instradare i job flessibili...")
    decisions = decide(regions, jobs)

    print("Cronista: scrivo il report e aggiorno data.json per la dashboard...")
    data = write_report(regions, jobs, decisions)

    best = min(regions, key=lambda r: r["current_stress"])
    print(f"\nCiclo completato. Regione a minor stress: {best['name']} ({best['current_stress']}%)")
    print(f"Litri stimati evitati (totale cumulativo): {data['liters_avoided_total']} L")


if __name__ == "__main__":
    main()
