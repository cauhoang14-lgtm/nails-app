import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURATION STYLE & DESSINS ---
st.set_page_config(page_title="Nails Manager Pro", page_icon="💅", layout="centered")

# STYLE CSS POUR LES ICÔNES ET BOUTONS
st.markdown("""
    <style>
    .main { background-color: #FDFEFE; }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        background-color: #8E44AD;
        color: white;
        font-weight: bold;
        border: none;
    }
    .metric-card {
        background-color: #F4ECF7;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #D7BDE2;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# LIEN GOOGLE SHEET
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSe5Y5nVHoX9XmZyAjE_Lf2u0hkWbGldKc-KdHmFPvZSkr2_vp8VzJWHCxtXiOfKPUMjcJzjnA2hK-m/pub?output=csv"

def get_users_data():
    try:
        user_df = pd.read_csv(SHEET_URL)
        data = {}
        for _, row in user_df.iterrows():
            uid = str(row.iloc[0]).lower().strip()
            pwd = str(row.iloc[1]).strip()
            try:
                val = float(str(row.iloc[2]).replace(',', '.'))
                pct = val / 100 if val > 1 else val
            except: pct = 0.5
            data[uid] = {"pwd": pwd, "pct": pct}
        return data
    except: return {"hoang": {"pwd": "1963", "pct": 0.5}}

# --- LOGIQUE DE CONNEXION ---
if "auth" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🔐</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Nails Pro Login</h2>", unsafe_allow_html=True)
    u = st.text_input("👤 Identifiant").lower().strip()
    p = st.text_input("🔑 Code Secret", type="password").strip()
    if st.button("ACCÉDER AU SALON"):
        users = get_users_data()
        if u in users and users[u]["pwd"] == p:
            st.session_state["auth"], st.session_state["pct"] = u, users[u]["pct"]
            st.rerun()
        else: st.error("Identifiant ou code incorrect.")

# --- INTERFACE PRINCIPALE ---
else:
    user, pct = st.session_state["auth"], st.session_state["pct"]
    st.markdown(f"<h2 style='text-align: center;'>✨ Chào {user.capitalize()}</h2>", unsafe_allow_html=True)
    
    DB_FILE = f"data_{user}.csv"
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=['Date', 'CA_Brut', 'Part'])

    # FORMULAIRE DE SAISIE
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>💅 Saisie Vente</h3>", unsafe_allow_html=True)
        dt = st.date_input("📅 Date", datetime.now())
        
        # Champ texte spécial pour le MICRO
        mt_txt = st.text_input("💰 Montant (€) - Utilisez le MICRO :", placeholder="Ex: 45")
        
        if st.button("💾 ENREGISTRER"):
            try:
                mt = float(mt_txt.replace(',', '.'))
                new_row = pd.DataFrame([{'Date': str(dt), 'CA_Brut': mt, 'Part': mt * pct}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.balloons()
                st.success(f"Enregistré ! Part : {mt * pct:.2f} €")
                st.rerun()
            except: st.error("Veuillez dire ou taper un chiffre.")

    st.divider()

    # TABLEAU DES RÉSULTATS (DESSINS)
    total_brut = df['CA_Brut'].sum() if not df.empty else 0
    total_part = df['Part'].sum() if not df.empty else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='metric-card'><h3>💰</h3><b>Total Brut</b><br><h2>{total_brut:.2f} €</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h3>💅</h3><b>Ma Part</b><br><h2>{total_part:.2f} €</h2></div>", unsafe_allow_html=True)

    if st.button("🚪 Déconnexion"):
        del st.session_state["auth"]
        st.rerun()
