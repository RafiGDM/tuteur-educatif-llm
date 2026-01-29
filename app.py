import streamlit as st
import requests
import json

st.set_page_config(page_title="Tuteur Éducatif", layout="centered")
st.title("Tuteur Éducatif Personnalisé")

# Interface
matiere = st.selectbox("Matière :", ["Programmation Python", "Algorithmique et structures de données"])
niveau = st.selectbox("Niveau :", ["Débutant", "Intermédiaire", "Avancé"])
question = st.text_area("Votre question :", placeholder="Explique les boucles en Python")

# 🔍 DEBUG 1 : Vérifiez si les secrets existent
st.sidebar.write("🔍 **DEBUG SECRETS**")
st.sidebar.write("Secrets disponibles:", list(st.secrets.keys()) if st.secrets else "Aucun")

# Token avec vérification
HF_API_TOKEN = st.secrets.get("HF_API_TOKEN") 

# 🔍 DEBUG 2 : Montrez le token (partiellement)
if HF_API_TOKEN:
    st.sidebar.write("✅ Token présent (premiers chars):", HF_API_TOKEN[:10] + "...")
else:
    st.sidebar.error("❌ Token NON trouvé dans st.secrets")

# Modèle
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}

def appeler_llm(prompt):
    try:
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 500, "temperature": 0.7}
        }
        st.sidebar.write("📡 Envoi à l'API...")
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        st.sidebar.write("📥 Réponse reçue, statut:", response.status_code)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if st.button("Obtenir l'explication"):
    if not HF_API_TOKEN:
        st.error("❌ Token Hugging Face manquant. Vérifiez les Secrets dans Streamlit Cloud.")
    elif not question.strip():
        st.warning("Entrez une question")
    else:
        prompt = f"""Explique {question} pour un niveau {niveau} en {matiere}"""
        
        with st.spinner("Génération en cours..."):
            resultat = appeler_llm(prompt)
        
        st.write("## Résultat brut de l'API :")
        st.json(resultat)
        
        if "error" in resultat:
            st.error(f"Erreur API: {resultat['error']}")
        elif isinstance(resultat, list) and len(resultat) > 0:
            if "generated_text" in resultat[0]:
                st.success("✅ Réponse générée :")
                st.write(resultat[0]["generated_text"])
            else:
                st.error("Format de réponse inconnu")
                st.write(resultat[0])
        else:
            st.error("Réponse vide ou format inattendu")