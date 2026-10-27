"""
Uses Groq (free tier) to analyse matches and produce ranked tips.
"""

from groq import Groq
from typing import List, Dict, Any
from config import GROQ_API_KEY, MAIN_TIPS, VALUE_TIPS
import json

client = Groq(api_key=GROQ_API_KEY)


SYSTEM_PROMPT = """Jesteś doświadczonym analitykiem zakładów bukmacherskich specjalizującym się w piłce nożnej.
Pracujesz wyłącznie na darmowych danych.

Dozwolone rynki:
- 1X2 (Home / Draw / Away)
- BTTS (Yes / No)
- Over/Under goli (np. Over 2.5, Under 2.5, Over 1.5, Under 3.5)
- Corners Over/Under
- Cards Over/Under

Zasady obowiązkowe:
1. Zwróć DOKŁADNIE 15 typów w "main_tips" (kursy 1.70–2.30) z lig głównych.
2. Zwróć DOKŁADNIE 5 typów w "value_tips" (kurs >= 3.00).
3. Zwróć DOKŁADNIE 15 typów w "other_leagues_tips" z pozostałych lig (jeśli są mecze).
4. Każdy typ MUSI mieć pola:
   - match (np. "Arsenal vs Chelsea")
   - market (np. "1X2", "BTTS", "Over/Under 2.5", "Corners Over 9.5", "Cards Over 3.5")
   - selection (np. "Home", "Draw", "Away", "Yes", "No", "Over", "Under")
   - odds (liczba, np. 1.95)
   - estimated_probability (liczba 0-100)
   - implied_probability (liczba 0-100)
   - justification (krótkie uzasadnienie po polsku)
5. NIGDY nie dawaj sprzecznych typów na ten sam mecz (np. Home i Away, Over i Under na tę samą linię).
6. Jeden mecz może mieć maksymalnie 2 typy, ale tylko jeśli rynki się nie wykluczają.
7. Odpowiedź WYŁĄCZNIE jako czysty JSON z kluczami: main_tips, value_tips, other_leagues_tips, summary.
"""


def build_user_prompt(matches: List[Dict]) -> str:
    if not matches:
        return "Brak meczów na dziś."

    main_leagues = {"PL", "PD", "BL1", "SA", "FL1", "CL", "EL", "DED", "PPL", "ELC"}
    main, other = [], []

    for m in matches:
        code = m.get("competition_code", "")
        line = f"- {m['home']} vs {m['away']} | {m['competition']} | {m['utc_date']}"
        if code in main_leagues:
            main.append(line)
        else:
            other.append(line)

    prompt = "Mecze z lig głównych (wyższa jakość analizy):\n"
    prompt += "\n".join(main) if main else "Brak"
    prompt += "\n\nMecze z innych lig (niższa jakość analizy):\n"
    prompt += "\n".join(other) if other else "Brak"
    prompt += "\n\nWygeneruj typy zgodnie z instrukcją systemową."
    return prompt


def analyse(matches: List[Dict]) -> Dict[str, Any]:
    if not matches:
        return {
            "main_tips": [],
            "value_tips": [],
            "other_leagues_tips": [],
            "summary": "Brak meczów na dziś.",
        }

    user_prompt = build_user_prompt(matches)

    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.35,
            max_tokens=5000,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        print("[DEBUG] Raw LLM response (first 2500 chars):")
        print(content[:2500])

        data = json.loads(content)

        return {
            "main_tips": data.get("main_tips", [])[:MAIN_TIPS],
            "value_tips": data.get("value_tips", [])[:VALUE_TIPS],
            "other_leagues_tips": data.get("other_leagues_tips", [])[:15],
            "summary": data.get("summary", ""),
        }
    except Exception as e:
        print(f"[ERROR] Groq analysis failed: {e}")
        return {
            "main_tips": [],
            "value_tips": [],
            "other_leagues_tips": [],
            "summary": f"Błąd analizy LLM: {str(e)}",
            "error": str(e),
        }
