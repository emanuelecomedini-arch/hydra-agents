"""
Sentinella — Agente dati.

Raccoglie segnali pubblici e gratuiti (meteo via Open-Meteo, nessuna chiave richiesta)
per stimare in modo illustrativo lo stress idrico corrente di ogni regione.

Nota di onestà, importante: questo NON è un dato ufficiale di stress idrico verificato.
È un proxy costruito da due elementi:
  1. una categoria di stress idrico di base per regione (baseline_stress in regions.json),
     ispirata nell'ordine di grandezza a indici pubblici come il WRI Aqueduct, ma codificata
     staticamente e non aggiornata automaticamente da quella fonte;
  2. un aggiustamento in base alle condizioni meteo del giorno (temperatura e precipitazioni),
     perché temperature alte e assenza di pioggia tendono a correlare con un maggiore stress
     idrico e maggiore necessità di raffreddamento.

Trattalo come una simulazione plausibile e trasparente, non come telemetria reale dei data
center: nessun operatore pubblica oggi quel dato in tempo reale.
"""
import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,precipitation",
        "daily": "precipitation_sum",
        "timezone": "auto",
        "forecast_days": 1,
    }
    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        temp = data.get("current", {}).get("temperature_2m")
        precip_now = data.get("current", {}).get("precipitation", 0)
        precip_day = (data.get("daily", {}).get("precipitation_sum") or [0])[0]
        return {
            "temperature_c": temp,
            "precipitation_today_mm": precip_day,
            "precipitation_now_mm": precip_now,
        }
    except Exception as e:
        return {"error": str(e)}


def adjust_stress(baseline_stress, weather):
    """Calcola uno stress corrente semplice a partire dal baseline e dal meteo del giorno."""
    if "error" in weather or weather.get("temperature_c") is None:
        return baseline_stress  # fallback: nessun aggiustamento se il meteo non è disponibile

    stress = baseline_stress
    temp = weather["temperature_c"]
    precip = weather["precipitation_today_mm"] or 0

    if temp >= 32:
        stress += 12
    elif temp >= 26:
        stress += 6
    elif temp <= 10:
        stress -= 5

    if precip <= 0.2:
        stress += 6
    elif precip >= 8:
        stress -= 10

    return max(3, min(97, round(stress)))


def collect(regions):
    """Arricchisce la lista statica di regioni con lo stress corrente stimato."""
    enriched = []
    for r in regions:
        weather = fetch_weather(r["lat"], r["lon"])
        current_stress = adjust_stress(r["baseline_stress"], weather)
        enriched.append({**r, "weather": weather, "current_stress": current_stress})
    return enriched
