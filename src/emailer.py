"""
Sends the daily report via Gmail SMTP using App Password.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from datetime import datetime
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT, WARSAW


def format_tip(tip: Dict, idx: int) -> str:
    """Pretty format a single tip."""
    match = tip.get("match") or tip.get("mecz") or "?"
    market = tip.get("market") or tip.get("rynek") or tip.get("selection") or "?"
    odds = tip.get("odds") or tip.get("kurs") or "?"
    prob = tip.get("estimated_probability") or tip.get("prawdopodobienstwo") or tip.get("prob") or "?"
    implied = tip.get("implied_probability") or tip.get("implied") or "?"
    reason = tip.get("justification") or tip.get("uzasadnienie") or tip.get("reason") or ""

    return (
        f"{idx}. {match}\n"
        f"   Rynek: {market}\n"
        f"   Kurs (szac.): {odds}  |  Twoje P: {prob}%  |  Implied: {implied}%\n"
        f"   Uzasadnienie: {reason}\n"
    )


def build_email_body(analysis: Dict[str, Any], matches_count: int) -> str:
    today = datetime.now(WARSAW).strftime("%d.%m.%Y")
    main_tips: List = analysis.get("main_tips", [])
    value_tips: List = analysis.get("value_tips", [])
    summary = analysis.get("summary", "")

    body = []
    body.append(f"Codzienne typy Superbet – {today}")
    body.append("=" * 50)
    body.append(f"Przeanalizowano meczów: {matches_count}")
    body.append("")

    if summary:
        body.append("Podsumowanie dnia:")
        body.append(summary)
        body.append("")

    body.append("-" * 50)
    body.append("15 NAJLEPSZYCH TYPÓW (kursy 1.70 – 2.30)")
    body.append("-" * 50)
    if main_tips:
        for i, tip in enumerate(main_tips, 1):
            body.append(format_tip(tip, i))
    else:
        body.append("Brak wygenerowanych typów w tym przedziale.")
    body.append("")

    body.append("-" * 50)
    body.append("5 TYPÓW VALUE (kurs >= 3.00)")
    body.append("-" * 50)
    if value_tips:
        for i, tip in enumerate(value_tips, 1):
            body.append(format_tip(tip, i))
    else:
        body.append("Brak wygenerowanych typów value.")
    body.append("")

    body.append("=" * 50)
    body.append("UWAGI:")
    body.append("- Kursy są szacunkowe / orientacyjne. Zawsze sprawdź aktualną ofertę na Superbet.pl")
    body.append("- To analiza automatyczna oparta o darmowe dane + LLM. Nie stanowi porady inwestycyjnej.")
    body.append("- Graj odpowiedzialnie.")
    body.append("")
    body.append("Agent wygenerowany automatycznie.")

    return "\n".join(body)


def send_email(analysis: Dict[str, Any], matches_count: int) -> bool:
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("[ERROR] Brak danych Gmail w sekretach")
        return False

    today = datetime.now(WARSAW).strftime("%d.%m.%Y")
    subject = f"Superbet typy na dziś – {today}"

    body = build_email_body(analysis, matches_count)

    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"[OK] Mail wysłany do {RECIPIENT}")
        return True
    except Exception as e:
        print(f"[ERROR] Nie udało się wysłać maila: {e}")
        return False
