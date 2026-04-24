# =============================================================
# app.py — Aplikacja Streamlit z suwakiem zakresu
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0f1117;
}
section[data-testid="stSidebar"] {
    background: #161b27;
    border-right: 1px solid #2a3142;
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# PASEK BOCZNY - WGRYWANIE PLIKÓW
# =============================================================
st.sidebar.title("⚙️ Ustawienia")

uploaded_matches = st.sidebar.file_uploader("1. Wgraj plik meczów (CSV/XLSX)", type=['csv', 'xlsx'])
uploaded_rules = st.sidebar.file_uploader("2. Wgraj plik reguł (XLSX)", type=['xlsx'])

# =============================================================
# GŁÓWNA SEKCJA
# =============================================================
st.title("📊 Symulator Strategii Zakładowych")

if uploaded_matches and uploaded_rules:
    # Wczytanie danych
    try:
        if uploaded_matches.name.endswith('.csv'):
            df_matches = pd.read_csv(uploaded_matches)
        else:
            df_matches = pd.read_excel(uploaded_matches)
            
        df_rules = pd.read_excel(uploaded_rules)
        
        total_matches = len(df_matches)
        
        st.info(f"Wczytano pomyślnie {total_matches} meczów.")

        # --- NOWOŚĆ: SUWAK ZAKRESU W GŁÓWNEJ CZĘŚCI ---
        st.subheader("🎯 Konfiguracja zakresu analizy")
        range_select = st.slider(
            "Wybierz zakres meczów do symulacji:",
            1, total_matches, (1, total_matches),
            help="Przesuń suwaki, aby wybrać od którego do którego meczu ma zostać przeprowadzona symulacja."
        )
        
        start_idx, end_idx = range_select
        st.write(f"Symulacja obejmie mecze od numeru **{start_idx}** do **{end_idx}** (łącznie: {end_idx - start_idx + 1}).")

        # Filtrowanie danych przed uruchomieniem
        filtered_matches = df_matches.iloc[start_idx-1 : end_idx].reset_index(drop=True)

        # Przycisk uruchomienia
        if st.button("🚀 Uruchom symulację na wybranym zakresie", use_container_width=True):
            with st.spinner("Trwa obliczanie wyników..."):
                sim_details, summary = run_simulation(filtered_matches, df_rules)
                st.session_state.sim_results = sim_details
                st.session_state.summary = summary
                st.success("Symulacja zakończona!")

        # Wyświetlanie wyników (jeśli istnieją w session_state)
        if 'summary' in st.session_state:
            tab1, tab2, tab3 = st.tabs(["📈 Wykresy", "📋 Tabela Wyników", "📥 Eksport"])
            
            with tab1:
                st.subheader("Porównanie ROI (%)")
                # Sprawdzamy czy kolumna 'roi' na pewno istnieje w podsumowaniu
                if 'roi' in st.session_state.summary.columns:
                    fig_roi = px.bar(
                        st.session_state.summary, 
                        x='rule_name', 
                        y='roi', 
                        color='roi',
                        color_continuous_scale='RdYlGn', 
                        title="ROI per Reguła"
                    )
                    st.plotly_chart(fig_roi, use_container_width=True)
                else:
                    st.error("Nie znaleziono kolumny ROI w wynikach symulacji.")
                
            with tab2:
                st.dataframe(st.session_state.summary.style.background_gradient(subset=['roi'], cmap='RdYlGn'), use_container_width=True)
                
            with tab3:
                st.write("Tutaj możesz pobrać wygenerowane raporty.")
                # (W Twoim oryginalnym kodzie były tu przyciski eksportu)

    except Exception as e:
        st.error(f"Wystąpił błąd podczas przetwarzania plików: {e}")
else:
    st.warning("Proszę wgrać oba pliki w panelu bocznym, aby odblokować opcje symulacji.")
