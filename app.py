
    
  import streamlit as st
import pandas as pd
import numpy as np

# 1. Konfiguracja interfejsu QUANT MATRIX PRO
st.set_page_config(page_title="QUANTUM SYNDICATE GLOBAL", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .stMetric div { color: #ffffff !important; }
    div.stButton > button:first-child { background-color: #3b82f6; color: white; width: 100%; border-radius: 5px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 QUANTUM SYNDICATE — GLOBAL ENGINE")
st.subheader("Model przetwarza pełną, globalną bazę danych ATP i Challenger z repozytoriów danych.")

# Łączymy stabilne bazy danych, aby ominać błąd braku pliku 2026
@st.cache_data(ttl=3600)
def load_global_data():
    try:
        # Ładujemy pełną bazę z ostatniego kompletnego sezonu
        url_2025 = "https://githubusercontent.com"
        df = pd.read_csv(url_2025)
        return df
    except Exception as e:
        st.error(f"Błąd krytyczny pobierania danych: {e}")
        return None

df_matches = load_global_data()

if df_matches is not None:
    st.success(f"🎯 Sukces! Załadowano globalną bazę danych online. Wykryto {len(df_matches)} rozegranych meczów z oficjalnego repozytorium!")

def get_player_surface_stats(player_name, df, surface_type):
    if df is None:
        return None
    name_upper = player_name.strip().upper()
    df_surface = df[df['surface'].str.upper() == surface_type.upper()]
    
    player_games = df_surface[(df_surface['winner_name'].str.upper().str.contains(name_upper, na=False)) | 
                              (df_surface['loser_name'].str.upper().str.contains(name_upper, na=False))]
    
    if len(player_games) < 2:
        return None
        
    wins = len(df_surface[df_surface['winner_name'].str.upper().str.contains(name_upper, na=False)])
    match_count = len(player_games)
    
    base_elo = 1500.0 + (wins * 18.0) - ((match_count - wins) * 14.0)
    win_ratio = wins / match_count
    calculated_dr = 1.0 + (win_ratio - 0.5) * 0.38
    
    # Bezpieczne pobranie nazwy wyświetlanej
    row = player_games.iloc[0]
    display_name = row['winner_name'] if name_upper in str(row['winner_name']).upper() else row['loser_name']
    
    return {
        "name": display_name,
        "elo": base_elo, 
        "dr": max(0.82, min(1.28, calculated_dr)), 
        "matches": match_count, 
        "wins": wins
    }

# 3. Sidebar Panel wejściowy
st.sidebar.header("🎛️ Panel Sterowania")
surface = st.sidebar.selectbox("Nawierzchnia meczu", ["Clay", "Hard"])
p1_input = st.sidebar.text_input("Nazwisko Zawodnika A (np. Ruud)", "Ruud")
p2_input = st.sidebar.text_input("Nazwisko Zawodnika B (np. Tsitsipas)", "Tsitsipas")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Kursy Bukmacherskie (1/2)")
odds_p1 = st.sidebar.number_input("Kurs na Zawodnika A", value=1.40, min_value=1.01, step=0.05)
odds_p2 = st.sidebar.number_input("Kurs na Zawodnika B", value=3.00, min_value=1.01, step=0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏦 Zarządzanie Stawką")
bankroll = st.sidebar.number_input("Twój budżet (zł)", value=1000.0, step=50.0)

submit = st.sidebar.button("🚀 URUCHOM GLOBALNĄ MATRIX 360°")

# 4. Sekcja Obliczeń
if submit and df_matches is not None:
    p1_stats = get_player_surface_stats(p1_input, df_matches, surface)
    p2_stats = get_player_surface_stats(p2_input, df_matches, surface)
    
    if p1_stats is None or p2_stats is None:
        st.error("❌ Model nie znalazł jednego z graczy. Wpisz samo nazwisko bez polskich znaków (np. Hurkacz, Djokovic).")
    else:
        elo_diff = p1_stats['elo'] - p2_stats['elo']
        prob_p1_base = 1.0 / (1.0 + 10.0 ** (-elo_diff / 400.0))
        prob_p1 = max(0.05, min(0.95, prob_p1_base * (p1_stats['dr'] / p2_stats['dr'])))
        prob_p2 = 1.0 - prob_p1
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### 📊 Profil: {p1_stats['name'].upper()}")
            st.write(f"Mecze w bazie: *{p1_stats['matches']}* (Wygrane: {p1_stats['wins']})")
            st.metric("Dynamiczne Surface Elo", f"{p1_stats['elo']:.1f}")
            st.metric("Dominance Ratio (DR)", f"{p1_stats['dr']:.2f}")
            st.write(f"Prawdopodobieństwo: *{prob_p1*100:.1f}%*")
            st.write(f"Kurs sprawiedliwy: *{1.0/prob_p1:.2f}*")
        with c2:
            st.markdown(f"### 📊 Profil: {p2_stats['name'].upper()}")
            st.write(f"Mecze w bazie: *{p2_stats['matches']}* (Wygrane: {p2_stats['wins']})")
            st.metric("Dynamiczne Surface Elo", f"{p2_stats['elo']:.1f}")
            st.metric("Dominance Ratio (DR)", f"{p2_stats['dr']:.2f}")
            st.write(f"Prawdopodobieństwo: *{prob_p2*100:.1f}%*")
            st.write(f"Kurs sprawiedliwy: *{1.0/prob_p2:.2f}*")
            
        st.markdown("---")
        st.header("🎯 PROCENTOWY ROZKŁAD WYNIKÓW SETOWYCH")
        s2_0 = (prob_p1 ** 1.5) * 100
        s2_1 = (prob_p1 * prob_p2 * 1.2) * 100
        s0_2 = (prob_p2 ** 1.5) * 100
        s1_2 = (prob_p2 * prob_p1 * 1.2) * 100
        total_s = s2_0 + s2_1 + s0_2 + s1_2
        
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        col_s1.metric(f"2:0 dla {p1_stats['name']}", f"{(s2_0/total_s)*100:.1f}%")
        col_s2.metric(f"2:1 dla {p1_stats['name']}", f"{(s2_1/total_s)*100:.1f}%")
        col_s3.metric(f"0:2 dla {p2_stats['name']}", f"{(s0_2/total_s)*100:.1f}%")
        col_s4.metric(f"1:2 dla {p2_stats['name']}", f"{(s1_2/total_s)*100:.1f}%")
        
        st.markdown("---")
        st.header("⚖️ RYZYKO I REKOMENDACJA STAWKI:")
        edge_p1 = prob_p1 - (1.0 / odds_p1)
        edge_p2 = prob_p2 - (1.0 / odds_p2)
        
        def get_stake(prob, odds, b_roll):
            f = (prob * (odds - 1.0) - (1.0 - prob)) / (odds - 1.0)
            return float(f * b_roll * 0.2) if f > 0 else 0.0

        target_edge = 5.0 / 100.0
        if edge_p1 > target_edge:
            st.markdown(f"<h1 style='color:#10b981;'>🟢 GRAJ NA: {p1_stats['name'].upper()}</h1>", unsafe_allow_html=True)
            st.subheader(f"ZAGRAJ ZA: {get_stake(prob_p1, odds_p1, bankroll):.2f} zł")
        elif edge_p2 > target_edge:
            st.markdown(f"<h1 style='color:#10b981;'>🟢 GRAJ NA: {p2_stats['name'].upper()}</h1>", unsafe_allow_html=True)
            st.subheader(f"ZAGRAJ ZA: {get_stake(prob_p2, odds_p2, bankroll):.2f} zł")
        else:
            st.markdown("<h1 style='color:#ef4444;'>🛑 ABSOLUTNY ZAKAZ GRY W TYM MECZU</h1>", unsafe_allow_html=True)
            st.subheader("Brak przewagi matematycznej. Stawka: 0.00 zł.")
