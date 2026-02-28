import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- RECOUVREMENT DES ERREURS DE MODULES ---
try:
    import altair as alt
except ImportError:
    pass

# --- CONFIGURATION ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSe5Y5nVHoX9XmZyAjE_Lf2u0hkWbGldKc-KdHmFPvZSkr2_vp8VzJWHCxtXiOfKPUMjcJzjnA2hK-m/pub?output=csv"

st.set_page_config(page_title="Nails App", layout="centered")

# --- CHARGEMENT DES DONNÉES ---
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
    except:
        return {"hoang": {"pwd": "1963", "pct": 0.5}}

# --- CONNEXION ---
if "auth" not in st.session_state:
    st.title("🔐 Đăng nhập")
    users = get_users_data()
    u = st.text_input("Tên đăng nhập :").lower().strip()
    p = st.text_input("Mật khẩu :", type="password").strip()
    
    if st.button("Đăng nhập", use_container_width=True):
        if u in users and users[u]["pwd"] == p:
            st.session_state["auth"] = u
            st.session_state["pct"] = users[u]["pct"]
            st.rerun()
        else:
            st.error("Sai tên đăng nhập hoặc mật khẩu.")

# --- INTERFACE ---
else:
    user = st.session_state["auth"]
    pct = st.session_state["pct"]
    
    st.title(f"💅 Chào {user.capitalize()}")
    st.write(f"Mức hưởng: **{int(pct*100)}%**")
    
    DB_FILE = f"data_{user}.csv"
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
    else:
        df = pd.DataFrame(columns=['Date', 'CA_Brut', 'Part'])

    with st.container(border=True):
        st.subheader("Nhập số liệu")
        dt = st.date_input("Ngày :", datetime.now())
        mt = st.number_input("Số tiền (€) :", min_value=0.0, format="%.2f")
        
        if st.button("LƯU DỮ LIỆU", use_container_width=True):
            if mt > 0:
                new_row = pd.DataFrame([{'Date': str(dt), 'CA_Brut': mt, 'Part': mt * pct}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("Đã lưu thành công!")
                st.rerun()

    st.divider()
    total = df['Part'].sum() if not df.empty else 0
    st.metric(label="Tổng thu nhập (Part)", value=f"{total:.2f} €")
    
    if st.button("Thoát (Déconnexion)"):
        del st.session_state["auth"]
        st.rerun()
