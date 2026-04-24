# Symulator Strategii Zakładowych

Aplikacja webowa do symulacji strategii zakładów sportowych.
Silnik obsługuje strategie STATE i CLASSIC z pełnym raportem ROI, drawdown i hit rate.

---

## Jak uruchomić na Streamlit Cloud (bez instalacji)

### Krok 1 — Załóż konto GitHub
Wejdź na https://github.com i załóż darmowe konto jeśli jeszcze nie masz.

### Krok 2 — Utwórz nowe repozytorium
1. Kliknij zielony przycisk **New** (lub **+** w prawym górnym rogu → New repository)
2. Nazwa: np. `symulator-zakladow`
3. Ustaw jako **Public**
4. Kliknij **Create repository**

### Krok 3 — Wgraj pliki do repozytorium
Wgraj wszystkie 4 pliki z tego archiwum:
- `app.py`
- `simulation.py`
- `requirements.txt`
- `rules.xlsx`

Jak wgrać: na stronie repozytorium kliknij **Add file → Upload files**, przeciągnij wszystkie 4 pliki, kliknij **Commit changes**.

### Krok 4 — Załóż konto Streamlit Cloud
Wejdź na https://streamlit.io/cloud i zaloguj się przez GitHub (kliknij **Continue with GitHub**).

### Krok 5 — Uruchom aplikację
1. Kliknij **New app**
2. Wybierz swoje repozytorium (`symulator-zakladow`)
3. W polu **Main file path** wpisz: `app.py`
4. Kliknij **Deploy**

Po około 60 sekundach aplikacja jest dostępna pod adresem:
`https://[twoja-nazwa].streamlit.app`

Ten link możesz udostępnić komukolwiek — działa w każdej przeglądarce.

---

## Jak używać aplikacji

1. **Zakładka "Dane wejściowe"** — wgraj plik meczów i plik reguł (rules.xlsx)
2. **Kliknij "Uruchom symulację"** w lewym panelu
3. **Zakładka "Wyniki"** — tabela z ROI, zyskiem, drawdown dla każdej reguły
4. **Zakładka "Wykresy"** — wybierz reguły do porównania na interaktywnym wykresie
5. **Zakładka "Eksport"** — pobierz wyniki jako Excel lub CSV

---

## Wymagane kolumny w pliku meczów

| Kolumna | Opis |
|---|---|
| match_no | Numer meczu |
| team_side | HOME lub AWAY |
| team_goals | Gole drużyny |
| opponent_goals | Gole przeciwnika |

---

## Struktura plików

```
app.py            ← główna aplikacja (interfejs)
simulation.py     ← silnik symulacji (logika)
requirements.txt  ← biblioteki Python
rules.xlsx        ← definicje reguł
```
