import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURATION DU LIEN GOOGLE ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSe5Y5nVHoX9XmZyAjE_Lf2u0hkWbGldKc-KdHmFPvZSkr2_vp8VzJWHCxtXiOfKPUMjcJzjnA2hK-m/pub?output=csv"

st.set_page_config(page_title="Nails App", page_icon="💅", layout="centered")

# --- STYLE CSS POUR L'INTERFACE MOBILE ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    .stTextInput>div>div>input {
        border-radius: 15px;
    }
    .stDateInput>div>div>input {
        border-radius: 15px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 40px;
        color: #ff4b4b;
    }
    .user-card {
        padding: 20px;
        background: white;
        border-radius: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

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

# --- LOGIQUE DE CONNEXION ---
if "auth" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>🔐 Đăng nhập</h1>", unsafe_allow_html=True)
    users = get_users_data()
    
    with st.container():
        u = st.text_input("Tên đăng nhập :").lower().strip()
        p = st.text_input("Mật khẩu :", type="password").strip()
        if st.button("ĐĂNG NHẬP"):
            if u in users and users[u]["pwd"] == p:
                st.session_state["auth"] = u
                st.session_state["pct"] = users[u]["pct"]
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu.")

# --- INTERFACE UTILISATEUR ---
else:
    user = st.session_state["auth"]
    pct = st.session_state["pct"]
    
    # En-tête élégant
    st.markdown(f"""
        <div class="user-card">
            <h2 style='margin:0;'>💅 Chào {user.capitalize()}</h2>
            <p style='color: gray;'>Mức hưởng của bạn: {int(pct*100)}%</p>
        </div>
    """, unsafe_allow_html=True)
    
    DB_FILE = f"data_{user}.csv"
    df = pd.read_csv(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame(columns=['Date', 'CA_Brut', 'Part'])

    # Formulaire de saisie
    with st.expander("➕ Nhập doanh thu mới", expanded=True):
        dt = st.date_input("Ngày :", datetime.now())
        mt_input = st.text_input("Số tiền (€) - Bấm 🎙️ để nói", placeholder="Ví dụ: 50")
        
        if st.button("LƯU DỮ LIỆU"):
            try:
                mt = float(mt_input.replace(',', '.'))
                if mt > 0:
                    new_row = pd.DataFrame([{'Date': str(dt), 'CA_Brut': mt, 'Part': mt * pct}])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success(f"Đã lưu: +{mt * pct:.2f} €")
                    st.rerun()
            except:
                st.error("Vui lòng nhập số tiền hợp lệ.")

    # Résumé financier
    st.markdown("---")
    total = df['Part'].sum() if not df.empty else 0
    st.metric(label="TỔNG THU NHẬP CỦA BẠN", value=f"{total:.2f} €")
    
    # Bouton de sortie discret
    if st.button("Thoát ứng dụng", key="logout"):
        del st.session_state["auth"]
        st.rerun()
