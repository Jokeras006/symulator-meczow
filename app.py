# =============================================================
# app.py — Aplikacja Streamlit
# Uruchomienie: streamlit run app.py
# =============================================================

import io
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from simulation import run_simulation

# =============================================================
# KONFIGURACJA STRONY
# =============================================================
st.set_page_config(
    page_title="Symulator Strategii",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================
# STYLE CSS
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Tło aplikacji */
.stApp {
    background: #0f1117;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #161b27;
    border-right: 1px solid #2a3142;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: #8892a4;
    font-size: 12px;
}

/* Nagłówek główny */
.main-header {
    background: linear-gradient(135deg, #1a2540 0%, #0f1117 100%);
    border: 1px solid #2a3142;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.main-header h1 {
    color: #e8ecf4;
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.main-header p {
    color: #5a6478;
    font-size: 13px;
    margin: 0;
}
.main-header .accent {
    color: #4d9de0;
}

/* Karty KPI */
.kpi-card {
    background: #161b27;
    border: 1px solid #2a3142;
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
}
.kpi-value {
    font-family: 'DM Mono', monospace;
    font-size: 28px;
    font-weight: 500;
    line-height: 1.1;
    margin-bottom: 4px;
}
.kpi-label {
    color: #5a6478;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.kpi-positive { color: #3dd68c; }
.kpi-negative { color: #ff6b6b; }
.kpi-neutral  { color: #4d9de0; }

/* Tabela wyników */
.results-header {
    color: #8892a4;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
}

/* Sekcja */
.section-title {
    color: #e8ecf4;
    font-size: 15px;
    font-weight: 600;
    margin: 0 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #2a3142;
}

/* Badge engine */
.badge-state   { background:#1e3a5f; color:#4d9de0; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600; }
.badge-classic { background:#2d1f3f; color:#a78bfa; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600; }

/* Upload area */
.upload-box {
    background: #161b27;
    border: 1px dashed #2a3142;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    color: #5a6478;
    font-size: 13px;
}

/* Alerty */
.alert-success {
    background: #0d2818;
    border: 1px solid #1a5c35;
    border-radius: 8px;
    padding: 12px 16px;
    color: #3dd68c;
    font-size: 13px;
}
.alert-error {
    background: #2d0f0f;
    border: 1px solid #6b1f1f;
    border-radius: 8px;
    padding: 12px 16px;
    color: #ff6b6b;
    font-size: 13px;
}
.alert-warning {
    background: #2d2400;
    border: 1px solid #6b5c00;
    border-radius: 8px;
    padding: 12px 16px;
    color: #ffd166;
    font-size: 13px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #161b27;
    border-radius: 8px;
    padding: 4px;
    border: 1px solid #2a3142;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #5a6478;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #1a2540 !important;
    color: #e8ecf4 !important;
}

/* Dataframe */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Przyciski */
.stButton > button {
    background: #1a2d4f;
    color: #4d9de0;
    border: 1px solid #2a4a7f;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 20px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #223660;
    border-color: #4d9de0;
    color: #7ab8ea;
}

/* Download button */
.stDownloadButton > button {
    background: #0d2818;
    color: #3dd68c;
    border: 1px solid #1a5c35;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
}

/* Divider */
hr { border-color: #2a3142; }
</style>
""", unsafe_allow_html=True)


# =============================================================
# POMOCNICZE FUNKCJE UI
# =============================================================

def fmt_profit(val):
    """Formatuje zysk z kolorem."""
    color = "#3dd68c" if val >= 0 else "#ff6b6b"
    sign  = "+" if val > 0 else ""
    return f'<span style="color:{color};font-family:DM Mono,monospace;font-weight:500">{sign}{val:.2f}</span>'

def fmt_roi(val):
    color = "#3dd68c" if val >= 0 else "#ff6b6b"
    sign  = "+" if val > 0 else ""
    return f'<span style="color:{color};font-family:DM Mono,monospace;font-weight:500">{sign}{val:.4f}</span>'

def fmt_side(val):
    colors = {"HOME": "#f0a500", "AWAY": "#4d9de0", "BOTH": "#a78bfa"}
    c = colors.get(str(val).upper(), "#8892a4")
    return f'<span style="color:{c};font-weight:600">{val}</span>'

def build_excel_export(sim_results, summary):
    """Buduje plik Excel w pamięci i zwraca bajty."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        summary.to_excel(writer, sheet_name="summary",  index=False)
        sim_results.to_excel(writer, sheet_name="details", index=False)

        waiting = summary[summary['rule_name'].str.contains('3LEVEL|WAITING', na=False)]
        win1    = summary[summary['rule_name'].str.contains('WIN1', na=False) &
                          ~summary['rule_name'].str.contains('3LEVEL|WAITING', na=False)]
        lose1   = summary[summary['rule_name'].str.contains('LOSE1', na=False) &
                          ~summary['rule_name'].str.contains('3LEVEL|WAITING', na=False)]

        if not waiting.empty: waiting.to_excel(writer, sheet_name="waiting_variants", index=False)
        if not win1.empty:    win1.to_excel(writer, sheet_name="win1_variants",    index=False)
        if not lose1.empty:   lose1.to_excel(writer, sheet_name="lose1_variants",  index=False)
    return buf.getvalue()


# =============================================================
# NAGŁÓWEK
# =============================================================
st.markdown("""
<div class="main-header">
    <h1>📊 Symulator Strategii Zakładowych</h1>
    <p>Wgraj dane meczów i reguły, uruchom symulację i przeanalizuj wyniki.
    Silnik obsługuje strategie <span class="accent">STATE</span> i <span class="accent">CLASSIC</span>
    z pełnym raportem ROI, drawdown i hit rate.</p>
</div>
""", unsafe_allow_html=True)


# =============================================================
# SIDEBAR — wgrywanie plików
# =============================================================
with st.sidebar:
    st.markdown("### 📁 Dane wejściowe")
    st.markdown("---")

    matches_file = st.file_uploader(
        "Plik meczów (.xlsx)",
        type=["xlsx"],
        help="Wymagane kolumny: match_no, team_side, team_goals, opponent_goals"
    )
    rules_file = st.file_uploader(
        "Plik reguł (.xlsx)",
        type=["xlsx"],
        help="Plik rules.xlsx z definicjami reguł"
    )

    st.markdown("---")

    run_btn = st.button("▶  Uruchom symulację", use_container_width=True)

    st.markdown("---")
    st.markdown("### ⚙️ Filtry wyników")

    filter_engine = st.multiselect(
        "Silnik", ["STATE", "CLASSIC"], default=["STATE", "CLASSIC"]
    )
    filter_side = st.multiselect(
        "Strona", ["BOTH", "HOME", "AWAY"], default=["BOTH", "HOME", "AWAY"]
    )
    only_positive = st.checkbox("Tylko zyskowne (ROI ≥ 0)", value=False)

    st.markdown("---")
    st.markdown(
        '<p style="color:#3a4258;font-size:11px;text-align:center">'
        'Symulator v2.0 · Silnik STATE + CLASSIC</p>',
        unsafe_allow_html=True
    )


# =============================================================
# STAN SESJI
# =============================================================
if "sim_results" not in st.session_state:
    st.session_state.sim_results = None
if "summary"     not in st.session_state:
    st.session_state.summary     = None
if "matches_df"  not in st.session_state:
    st.session_state.matches_df  = None
if "rules_df"    not in st.session_state:
    st.session_state.rules_df    = None


# =============================================================
# WCZYTANIE PLIKÓW
# =============================================================
if matches_file:
    try:
        st.session_state.matches_df = pd.read_excel(matches_file, engine='openpyxl')
    except Exception as e:
        st.sidebar.error(f"Błąd pliku meczów: {e}")

if rules_file:
    try:
        st.session_state.rules_df = pd.read_excel(rules_file, engine='openpyxl')
    except Exception as e:
        st.sidebar.error(f"Błąd pliku reguł: {e}")


# =============================================================
# URUCHOMIENIE SYMULACJI
# =============================================================
if run_btn:
    if st.session_state.matches_df is None or st.session_state.rules_df is None:
        st.warning("⚠️ Wgraj oba pliki przed uruchomieniem symulacji.")
    else:
        with st.spinner("Trwa symulacja..."):
            try:
                sim, summ = run_simulation(
                    st.session_state.matches_df,
                    st.session_state.rules_df
                )
                st.session_state.sim_results = sim
                st.session_state.summary     = summ
                st.sidebar.markdown(
                    '<div class="alert-success">✅ Symulacja zakończona pomyślnie.</div>',
                    unsafe_allow_html=True
                )
            except ValueError as e:
                st.error(f"❌ Błąd konfiguracji:\n\n{e}")
            except Exception as e:
                st.error(f"❌ Nieoczekiwany błąd: {e}")


# =============================================================
# ZAKŁADKI
# =============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📋  Dane wejściowe",
    "📈  Wyniki symulacji",
    "📉  Wykresy",
    "💾  Eksport"
])


# ─────────────────────────────────────────────
# ZAKŁADKA 1 — Dane wejściowe
# ─────────────────────────────────────────────
with tab1:
    col_m, col_r = st.columns(2, gap="large")

    with col_m:
        st.markdown('<p class="section-title">Dane meczów</p>', unsafe_allow_html=True)
        if st.session_state.matches_df is not None:
            df = st.session_state.matches_df
            st.markdown(
                f'<div class="alert-success">✅ Wgrano {len(df)} meczów · '
                f'{df["team_side"].value_counts().get("HOME", 0)} domowych, '
                f'{df["team_side"].value_counts().get("AWAY", 0)} wyjazdowych</div>',
                unsafe_allow_html=True
            )
            st.dataframe(df, use_container_width=True, height=320)
        else:
            st.markdown(
                '<div class="upload-box">👈 Wgraj plik meczów w sidebarze</div>',
                unsafe_allow_html=True
            )

    with col_r:
        st.markdown('<p class="section-title">Reguły</p>', unsafe_allow_html=True)
        if st.session_state.rules_df is not None:
            df_r = st.session_state.rules_df
            active = df_r[df_r['active'].astype(str).str.upper().isin(['YES','1'])]
            st.markdown(
                f'<div class="alert-success">✅ Wgrano {len(df_r)} reguł · '
                f'{len(active)} aktywnych</div>',
                unsafe_allow_html=True
            )
            st.dataframe(df_r, use_container_width=True, height=320)
        else:
            st.markdown(
                '<div class="upload-box">👈 Wgraj plik reguł w sidebarze</div>',
                unsafe_allow_html=True
            )


# ─────────────────────────────────────────────
# ZAKŁADKA 2 — Wyniki symulacji
# ─────────────────────────────────────────────
with tab2:
    if st.session_state.summary is None:
        st.markdown(
            '<div class="upload-box" style="margin-top:40px">'
            '▶ Wgraj pliki i kliknij <b>Uruchom symulację</b>, aby zobaczyć wyniki.'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        summary = st.session_state.summary.copy()

        # Filtrowanie wg sidebar
        summary = summary[summary['engine'].isin(filter_engine)]
        summary = summary[summary['side'].isin(filter_side)]
        if only_positive:
            summary = summary[summary['roi'] >= 0]

        # ── KPI ──────────────────────────────────────────────
        total_rules    = len(summary)
        profitable     = (summary['roi'] >= 0).sum()
        best_roi       = summary['roi'].max()
        best_rule      = summary.loc[summary['roi'].idxmax(), 'rule_id'] if total_rules > 0 else "—"
        total_profit   = summary['total_profit'].sum()
        avg_hit        = summary['hit_rate'].mean()

        k1, k2, k3, k4, k5 = st.columns(5)
        kpis = [
            (k1, str(total_rules),          "Reguły",             "kpi-neutral"),
            (k2, f"{profitable}/{total_rules}", "Zyskowne",        "kpi-positive" if profitable > 0 else "kpi-negative"),
            (k3, f"{best_roi:+.4f}",        f"Najlepszy ROI ({best_rule})", "kpi-positive" if best_roi >= 0 else "kpi-negative"),
            (k4, f"{total_profit:+.2f} zł", "Łączny P&L",        "kpi-positive" if total_profit >= 0 else "kpi-negative"),
            (k5, f"{avg_hit:.1f}%",         "Średni Hit Rate",    "kpi-neutral"),
        ]
        for col, val, label, css in kpis:
            with col:
                st.markdown(
                    f'<div class="kpi-card">'
                    f'<div class="kpi-value {css}">{val}</div>'
                    f'<div class="kpi-label">{label}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Tabela ───────────────────────────────────────────
        st.markdown('<p class="section-title">Tabela wyników</p>', unsafe_allow_html=True)

        display_cols = [
            'rule_id', 'rule_name', 'side', 'engine',
            'matches', 'active_matches', 'hits', 'hit_rate',
            'total_profit', 'avg_stake', 'roi', 'max_drawdown', 'max_streak'
        ]
        display_cols = [c for c in display_cols if c in summary.columns]

        st.dataframe(
            summary[display_cols].style
                .background_gradient(subset=['roi'],          cmap='RdYlGn', vmin=-0.5, vmax=0.5)
                .background_gradient(subset=['total_profit'], cmap='RdYlGn')
                .background_gradient(subset=['hit_rate'],     cmap='Blues', vmin=0, vmax=100)
                .format({
                    'total_profit': '{:+.2f}',
                    'roi':          '{:+.4f}',
                    'hit_rate':     '{:.1f}%',
                    'avg_stake':    '{:.1f}',
                    'max_drawdown': '{:.2f}',
                }),
            use_container_width=True,
            height=520
        )

        # ── Szczegóły wybranej reguły ─────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-title">Szczegóły reguły</p>', unsafe_allow_html=True)

        rule_ids = st.session_state.summary['rule_id'].tolist()
        selected_rule = st.selectbox("Wybierz regułę do podglądu szczegółów:", rule_ids)

        if selected_rule:
            detail = st.session_state.sim_results[
                st.session_state.sim_results['rule_id'] == selected_rule
            ]
            st.dataframe(detail, use_container_width=True, height=300)


# ─────────────────────────────────────────────
# ZAKŁADKA 3 — Wykresy
# ─────────────────────────────────────────────
with tab3:
    if st.session_state.sim_results is None:
        st.markdown(
            '<div class="upload-box" style="margin-top:40px">'
            '▶ Uruchom symulację, aby zobaczyć wykresy.</div>',
            unsafe_allow_html=True
        )
    else:
        sim     = st.session_state.sim_results
        summary = st.session_state.summary

        st.markdown('<p class="section-title">Wykres salda skumulowanego</p>',
                    unsafe_allow_html=True)

        # Wybór reguł do wykresu
        all_ids    = sorted(summary['rule_id'].tolist())
        default_ids = summary.nlargest(6, 'roi')['rule_id'].tolist()

        selected_ids = st.multiselect(
            "Wybierz reguły do porównania (max 15):",
            options=all_ids,
            default=default_ids,
            max_selections=15
        )

        if selected_ids:
            fig = go.Figure()

            # Paleta kolorów
            palette = px.colors.qualitative.Plotly + px.colors.qualitative.Dark24

            for i, rule_id in enumerate(selected_ids):
                subset = sim[sim['rule_id'] == rule_id].reset_index(drop=True)
                if subset.empty: continue

                rule_info = summary[summary['rule_id'] == rule_id]
                roi_val   = rule_info['roi'].values[0] if not rule_info.empty else 0
                side_val  = rule_info['side'].values[0] if not rule_info.empty else ""

                fig.add_trace(go.Scatter(
                    x    = list(range(len(subset))),
                    y    = subset['running_balance'],
                    mode = 'lines',
                    name = f"[{rule_id}] {side_val} (ROI: {roi_val:+.3f})",
                    line = dict(color=palette[i % len(palette)], width=2),
                    hovertemplate=(
                        f"<b>{rule_id}</b><br>"
                        "Mecz: %{x}<br>"
                        "Saldo: %{y:.2f} zł<br>"
                        "<extra></extra>"
                    )
                ))

            fig.add_hline(y=0, line_dash="dash", line_color="#3a4258", line_width=1.5)

            fig.update_layout(
                paper_bgcolor = "#0f1117",
                plot_bgcolor  = "#161b27",
                font          = dict(family="DM Sans", color="#8892a4", size=12),
                legend        = dict(
                    bgcolor     = "#1a2030",
                    bordercolor = "#2a3142",
                    borderwidth = 1,
                    font        = dict(size=11)
                ),
                xaxis = dict(
                    title      = "Numer meczu",
                    gridcolor  = "#1e2535",
                    showgrid   = True,
                    zeroline   = False,
                    tickfont   = dict(size=11)
                ),
                yaxis = dict(
                    title      = "Saldo skumulowane (zł)",
                    gridcolor  = "#1e2535",
                    showgrid   = True,
                    zeroline   = False,
                    tickfont   = dict(size=11),
                    tickformat = ",.0f"
                ),
                hovermode = "x unified",
                height    = 520,
                margin    = dict(l=60, r=20, t=30, b=60),
            )

            st.plotly_chart(fig, use_container_width=True)

        # ── Wykres słupkowy ROI ───────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-title">ROI wszystkich reguł</p>',
                    unsafe_allow_html=True)

        summary_filt = st.session_state.summary.copy()
        summary_filt = summary_filt[summary_filt['engine'].isin(filter_engine)]
        summary_filt = summary_filt[summary_filt['side'].isin(filter_side)]
        summary_filt = summary_filt.sort_values('roi', ascending=True)

        bar_colors = [
            "#3dd68c" if v >= 0 else "#ff6b6b"
            for v in summary_filt['roi']
        ]

        fig_bar = go.Figure(go.Bar(
            x           = summary_filt['roi'],
            y           = summary_filt['rule_id'],
            orientation = 'h',
            marker_color= bar_colors,
            text        = summary_filt['roi'].apply(lambda v: f"{v:+.4f}"),
            textposition= 'outside',
            textfont    = dict(size=10, color="#8892a4"),
            hovertemplate = (
                "<b>%{y}</b><br>"
                "ROI: %{x:.4f}<br>"
                "<extra></extra>"
            )
        ))

        fig_bar.add_vline(x=0, line_dash="dash", line_color="#3a4258", line_width=1.5)

        fig_bar.update_layout(
            paper_bgcolor = "#0f1117",
            plot_bgcolor  = "#161b27",
            font          = dict(family="DM Sans", color="#8892a4", size=11),
            xaxis = dict(
                title    = "ROI",
                gridcolor= "#1e2535",
                zeroline = False
            ),
            yaxis = dict(
                gridcolor= "#1e2535",
                zeroline = False,
                tickfont = dict(size=10)
            ),
            height = max(400, len(summary_filt) * 22),
            margin = dict(l=80, r=80, t=20, b=40),
        )

        st.plotly_chart(fig_bar, use_container_width=True)


# ─────────────────────────────────────────────
# ZAKŁADKA 4 — Eksport
# ─────────────────────────────────────────────
with tab4:
    if st.session_state.sim_results is None:
        st.markdown(
            '<div class="upload-box" style="margin-top:40px">'
            '▶ Uruchom symulację, aby pobrać wyniki.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<p class="section-title">Pobierz wyniki</p>',
                    unsafe_allow_html=True)

        col_a, col_b = st.columns(2, gap="large")

        with col_a:
            st.markdown("""
            <div style="background:#161b27;border:1px solid #2a3142;border-radius:10px;padding:24px">
                <div style="font-size:32px;margin-bottom:12px">📊</div>
                <div style="color:#e8ecf4;font-weight:600;font-size:15px;margin-bottom:6px">Excel — Pełny raport</div>
                <div style="color:#5a6478;font-size:12px;margin-bottom:20px">
                    Arkusze: summary, details, waiting_variants, win1_variants, lose1_variants
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            excel_bytes = build_excel_export(
                st.session_state.sim_results,
                st.session_state.summary
            )
            st.download_button(
                label     = "⬇  Pobierz Excel (.xlsx)",
                data      = excel_bytes,
                file_name = "simulation_results.xlsx",
                mime      = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col_b:
            st.markdown("""
            <div style="background:#161b27;border:1px solid #2a3142;border-radius:10px;padding:24px">
                <div style="font-size:32px;margin-bottom:12px">📋</div>
                <div style="color:#e8ecf4;font-weight:600;font-size:15px;margin-bottom:6px">CSV — Dane szczegółowe</div>
                <div style="color:#5a6478;font-size:12px;margin-bottom:20px">
                    Dane per mecz per reguła — do dalszej analizy w Excelu lub Python
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            csv_bytes = st.session_state.sim_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label     = "⬇  Pobierz CSV (details)",
                data      = csv_bytes,
                file_name = "simulation_details.csv",
                mime      = "text/csv",
                use_container_width=True
            )

        # ── Podgląd podsumowania ──────────────────────────────
        st.markdown("---")
        st.markdown('<p class="section-title">Podgląd — Summary</p>',
                    unsafe_allow_html=True)
        st.dataframe(st.session_state.summary, use_container_width=True, height=400)
