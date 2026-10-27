"""
Fetches today's fixtures + basic form from football-data.org (free tier).
Also attempts a light Superbet scrape for main markets (best-effort).
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
from config import FOOTBALL_DATA_TOKEN, COMPETITIONS, WARSAW

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": FOOTBALL_DATA_TOKEN}


def get_todays_matches() -> List[Dict[str, Any]]:
    """Return list of matches scheduled for today (Warsaw time) in free competitions."""
    today = datetime.now(WARSAW).date()
    date_from = today.isoformat()
    date_to = (today + timedelta(days=1)).isoformat()

    matches = []
    for code in COMPETITIONS:
        try:
            url = f"{BASE_URL}/competitions/{code}/matches"
            params = {
                "dateFrom": date_from,
                "dateTo": date_to,
                "status": "SCHEDULED",
            }
            r = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if r.status_code == 200:
                data = r.json()
                for m in data.get("matches", []):
                    matches.append({
                        "id": m["id"],
                        "competition": data.get("competition", {}).get("name") or code,
                        "competition_code": code,
                        "home": m["homeTeam"]["name"],
                        "away": m["awayTeam"]["name"],
                        "utc_date": m["utcDate"],
                        "status": m["status"],
                    })
            time.sleep(1.2)  # respect free tier rate limit (~10/min)
        except Exception as e:
            print(f"[WARN] Failed to fetch {code}: {e}")
            continue

    # Sort by kickoff
    matches.sort(key=lambda x: x["utc_date"])
    return matches


def get_team_form(team_id: int, limit: int = 5) -> Dict[str, Any]:
    """Very light form lookup (last finished matches)."""
    try:
        url = f"{BASE_URL}/teams/{team_id}/matches"
        params = {"status": "FINISHED", "limit": limit}
        r = requests.get(url, headers=HEADERS, params=params, timeout=12)
        if r.status_code != 200:
            return {}
        data = r.json()
        results = []
        for m in data.get("matches", []):
            if m["score"]["winner"] is None:
                continue
            is_home = m["homeTeam"]["id"] == team_id
            winner = m["score"]["winner"]
            if winner == "DRAW":
                results.append("D")
            elif (winner == "HOME_TEAM" and is_home) or (winner == "AWAY_TEAM" and not is_home):
                results.append("W")
            else:
                results.append("L")
        return {"last_results": "".join(results), "matches_count": len(results)}
    except Exception:
        return {}


def enrich_matches_with_basic_info(matches: List[Dict]) -> List[Dict]:
    """Add very basic info. We keep it light because of free rate limits."""
    enriched = []
    for m in matches:
        # football-data free tier does not always give team ids in the matches list in a convenient way
        # for deep enrichment, so we keep it simple for MVP
        enriched.append({
            **m,
            "markets_note": "1X2, BTTS, O/U, corners, cards – sprawdź aktualne kursy na Superbet.pl",
        })
    return enriched
