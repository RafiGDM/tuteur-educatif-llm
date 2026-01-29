import streamlit as st
import requests
import os

# -----------------------------
# CONFIGURATION DE LA PAGE
# -----------------------------
st.set_page_config(
    page_title="Tuteur Éducatif Personnalisé (LLM)",
    page_icon=" ",
    layout="centered"
)

st.title("Tuteur Éducatif Personnalisé")
st.write(
    "Ce tuteur utilise un **Large Language Model (LLM)** pour accompagner "
    "les étudiants de **Licence 3 Informatique** de manière personnalisée."
)

# -----------------------------
# PARAMÈTRES UTILISATEUR
# -----------------------------
matiere = st.selectbox(
    "Choisissez la matière :",
    ["Programmation Python", "Algorithmique et structures de données"]
)

niveau = st.selectbox(
    "Choisissez votre niveau :",
    ["Débutant", "Intermédiaire", "Avancé"]
)

question = st.text_area(
    "Posez votre question :",
    placeholder="Ex : Explique-moi les boucles en Python"
)

# -----------------------------
# CLÉ API HUGGING FACE
# -----------------------------
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

# -----------------------------
# FONCTION D'APPEL AU LLM
# -----------------------------
def appeler_llm(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# -----------------------------
# BOUTON DE GÉNÉRATION
# -----------------------------
if st.button("Obtenir l'explication"):

    if not HF_API_TOKEN:
        st.error("Clé API Hugging Face manquante.")
    elif question.strip() == "":
        st.warning("Veuillez entrer une question.")
    else:
        prompt = f"""
Tu es un tuteur éducatif universitaire pour un étudiant en Licence 3 Informatique.

Matière : {matiere}
Niveau de l'étudiant : {niveau}

Règles pédagogiques :
- Adapter le langage au niveau
- Expliquer progressivement
- Donner des exemples clairs
- Encourager l'étudiant
- Poser une question à la fin pour vérifier la compréhension

Question de l'étudiant :
{question}
"""

        with st.spinner("Génération de la réponse pédagogique..."):
            resultat = appeler_llm(prompt)

        if isinstance(resultat, list) and "generated_text" in resultat[0]:
            st.success("Réponse du tuteur")
            st.write(resultat[0]["generated_text"])
        else:
            st.error("Erreur lors de la génération de la réponse.")
