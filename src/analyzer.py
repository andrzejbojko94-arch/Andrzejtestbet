"""
Uses Groq (free tier) to analyse matches and produce ranked tips.
"""

from groq import Groq
from typing import List, Dict, Any
from config import GROQ_API_KEY, MIN_ODDS, MAX_ODDS, HIGH_ODDS_MIN, MAIN_TIPS, VALUE_TIPS
import json

client = Groq(api_key=GROQ_API_KEY)


SYSTEM_PROMPT = """Jesteś doświadczonym analitykiem zakładów bukmacherskich specjalizującym się w piłce nożnej.
Pracujesz wyłącznie na darmowych danych i rozsądnych założeniach.

Twoim zadaniem jest wybrać najlepsze typy na dziś z oferty zbliżonej do Superbet.pl.

Dozwolone rynki:
- 1X2 (zwycięzca meczu / remis)
- BTTS (obie drużyny strzelą – Tak/Nie)
- Powyżej / Poniżej liczby goli (główne linie 1.5, 2.5, 3.5)
- Liczba rzutów rożnych (powyżej/poniżej)
- Liczba kartek (powyżej/poniżej)

Zasady:
1. Główna lista: dokładnie 15 typów z kursami w przedziale 1.70 – 2.30.
2. Lista value: dokładnie 5 typów z kursem >= 3.00, gdzie widzisz realną wartość.
3. Do każdego typu podaj:
   - mecz
   - rynek i selekcję
   - szacowany kurs (realistyczny dla Superbet)
   - Twoje estymowane prawdopodobieństwo (w %)
   - implied probability bukmachera (1/kurs)
   - krótkie, konkretne uzasadnienie (formy, styl gry, motywacja, kontuzje jeśli znane, kontekst)
4. Bądź konserwatywny. Nie wymyślaj nieistniejących kontuzji.
5. Preferuj typy, które mają sens statystyczny i kontekstowy.
6. Odpowiedź zwróć WYŁĄCZNIE jako poprawny JSON (bez markdown, bez komentarzy).
"""


def build_user_prompt(matches: List[Dict]) -> str:
    if not matches:
        return "Brak meczów na dziś w monitorowanych ligach."

    lines = ["Mecze na dziś (piłka nożna):\n"]
    for i, m in enumerate(matches, 1):
        lines.append(
            f"{i}. {m['home']} vs {m['away']} | {m['competition']} | {m['utc_date']}"
        )
    lines.append(
        "\nNa podstawie powyższych meczów przygotuj ranking typów zgodnie z instrukcją systemową."
    )
    return "\n".join(lines)


def analyse(matches: List[Dict]) -> Dict[str, Any]:
    """Call Groq and return structured tips."""
    if not matches:
        return {
            "main_tips": [],
            "value_tips": [],
            "summary": "Brak meczów na dziś w monitorowanych ligach.",
        }

    user_prompt = build_user_prompt(matches)

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # aktualny darmowy model na Groq
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.35,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        data = json.loads(content)

        # Normalise keys
        main = data.get("main_tips") or data.get("typy_glowne") or data.get("tips") or []
        value = data.get("value_tips") or data.get("typy_value") or data.get("high_odds") or []

        return {
            "main_tips": main[:MAIN_TIPS],
            "value_tips": value[:VALUE_TIPS],
            "summary": data.get("summary") or data.get("podsumowanie") or "",
            "raw": data,
        }
    except Exception as e:
        print(f"[ERROR] Groq analysis failed: {e}")
        return {
            "main_tips": [],
            "value_tips": [],
            "summary": f"Błąd analizy LLM: {str(e)}",
            "error": str(e),
        }
