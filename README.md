# Superbet Daily Tips Agent (wersja darmowa)

Codzienny agent, który:

- Pobiera dzisiejsze mecze piłkarskie z darmowego API football-data.org
- Analizuje je przez LLM (Groq – darmowy tier)
- Generuje **15 typów** w kursach 1.70–2.30 + **5 typów value** (kurs ≥ 3.00)
- Wysyła raport mailem na `andrzej.bojko94@gmail.com` codziennie ok. 8:30 czasu polskiego

## Rynki brane pod uwagę
- 1X2
- BTTS (obie strzelą)
- Powyżej / Poniżej goli
- Liczba rzutów rożnych
- Liczba kartek

## Wymagane sekrety (GitHub → Settings → Secrets → Actions)

| Sekret                | Opis                          |
|-----------------------|-------------------------------|
| `GMAIL_ADDRESS`       | Twój adres Gmail              |
| `GMAIL_APP_PASSWORD`  | Hasło aplikacji Gmail         |
| `FOOTBALL_DATA_TOKEN` | Token z football-data.org     |
| `GROQ_API_KEY`        | Klucz API z console.groq.com  |

## Jak uruchomić ręcznie
1. Wejdź w zakładkę **Actions**
2. Wybierz workflow **Daily Superbet Tips**
3. Kliknij **Run workflow**

## Harmonogram
Workflow odpala się codziennie o **07:00 UTC** (ok. 08:00–09:00 czasu polskiego w zależności od DST).

## Ograniczenia wersji darmowej
- Kursy są **szacunkowe** (LLM + wiedza o typowych liniach). Zawsze weryfikuj na Superbet.pl.
- Tylko ligi dostępne w darmowym tierze football-data.org.
- Jakość zależy od aktualnego modelu na Groq i dostępnych danych.
- Nie stanowi porady inwestycyjnej. Graj odpowiedzialnie.

## Struktura
