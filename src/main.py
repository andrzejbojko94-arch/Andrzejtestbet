"""
Daily Superbet football tips agent (free tier version).
"""

import sys
import os

# Allow running from src/ or project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import get_todays_matches, enrich_matches_with_basic_info
from analyzer import analyse
from emailer import send_email
from config import today_warsaw


def main():
    print(f"=== Superbet Daily Tips – {today_warsaw()} ===")

    print("[1/4] Pobieram mecze na dziś...")
    matches = get_todays_matches()
    print(f"     Znaleziono {len(matches)} meczów w monitorowanych ligach.")

    if not matches:
        print("Brak meczów – wysyłam pusty raport.")
        analysis = {
            "main_tips": [],
            "value_tips": [],
            "summary": "Dziś brak meczów w monitorowanych ligach (top 5 + CL/EL + kilka innych).",
        }
        send_email(analysis, 0)
        return

    print("[2/4] Wzbogacam dane...")
    matches = enrich_matches_with_basic_info(matches)

    print("[3/4] Analizuję przez LLM (Groq)...")
    analysis = analyse(matches)

    print(f"     Główne typy: {len(analysis.get('main_tips', []))}")
    print(f"     Value typy:  {len(analysis.get('value_tips', []))}")

    print("[4/4] Wysyłam maila...")
    success = send_email(analysis, len(matches))

    if success:
        print("Gotowe.")
    else:
        print("Mail nie został wysłany – sprawdź sekrety i logi.")
        sys.exit(1)


if __name__ == "__main__":
    main()
