import streamlit as st

st.title("Test Salon Nails")
st.write("Bonjour Monseigneur Hoang !")
st.success("Si vous voyez ce message, l'application fonctionne !")

u = st.text_input("Nom :")
p = st.text_input("Code :", type="password")

if st.button("Valider"):
    st.write(f"Bravo {u}, le système est prêt.")
