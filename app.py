import streamlit as st
import requests
import json

st.set_page_config(page_title="Tuteur Éducatif", layout="centered")
st.title("Tuteur Éducatif Personnalisé")

# Interface
matiere = st.selectbox("Matière :", ["Programmation Python", "Algorithmique et structures de données"])
niveau = st.selectbox("Niveau :", ["Débutant", "Intermédiaire", "Avancé"])
question = st.text_area("Votre question :", placeholder="Explique les boucles en Python")

# Token
HF_API_TOKEN = st.secrets.get("HF_API_TOKEN")

# 🔴 CORRECTION ICI : NOUVELLE URL
API_URL = "https://router.huggingface.co/google/flan-t5-large"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def appeler_llm(prompt):
    try:
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 500, "temperature": 0.7}
        }
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if st.button("Obtenir l'explication"):
    if not HF_API_TOKEN:
        st.error("Token manquant")
    elif not question.strip():
        st.warning("Entrez une question")
    else:
        prompt = f"""Explique {question} pour un niveau {niveau} en {matiere}. 
        Sois pédagogique et donne des exemples."""
        
        with st.spinner("Génération en cours..."):
            resultat = appeler_llm(prompt)
        
        # 🔍 Debug
        st.write("Réponse brute de l'API :", resultat)
        
        if "error" in resultat:
            st.error(f"Erreur API: {resultat['error']}")
        elif isinstance(resultat, list) and len(resultat) > 0:
            if "generated_text" in resultat[0]:
                st.success("✅ Réponse :")
                st.write(resultat[0]["generated_text"])
            else:
                st.write("Contenu :", resultat[0])
        else:
            st.error("Format de réponse inattendu")