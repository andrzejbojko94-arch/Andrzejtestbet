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
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt + "\n\nWAŻNE: Musisz zwrócić DOKŁADNIE 15 typów w main_tips (kursy 1.70-2.30) oraz DOKŁADNIE 5 typów w value_tips (kurs >= 3.00). Nie zwracaj pustych list. Jeśli brakuje mocnych sygnałów – wybierz najlepsze dostępne."},
            ],
            temperature=0.4,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        print("[DEBUG] Raw LLM response:")
        print(content[:1500])  # logujemy początek odpowiedzi

        data = json.loads(content)

        # Bardziej odporne wyciąganie list
        main = (
            data.get("main_tips")
            or data.get("typy_glowne")
            or data.get("tips")
            or data.get("best_tips")
            or data.get("rekomendacje")
            or []
        )
        value = (
            data.get("value_tips")
            or data.get("typy_value")
            or data.get("high_odds")
            or data.get("value_bets")
            or []
        )

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
