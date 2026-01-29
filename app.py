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
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    matiere = st.selectbox(
        "Matière",
        ["Programmation Python", "Algorithmique et structures de données"]
    )

    niveau = st.selectbox(
        "Niveau",
        ["Débutant", "Intermédiaire", "Avancé"]
    )

with col2:
    question = st.text_area(
        "Question",
        placeholder="Ex : Explique les boucles en Python",
        height=150
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

API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.2"
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

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    # Vérifier le statut HTTP
    if response.status_code != 200:
        return {
            "error": f"HTTP {response.status_code} : {response.text}"
        }

    # Vérifier que la réponse est bien du JSON
    content_type = response.headers.get("Content-Type", "")

    if "application/json" in content_type:
        return response.json()
    else:
        return {
            "error": "Réponse non JSON reçue depuis Hugging Face",
            "raw_response": response.text[:500]
        }



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

        # -----------------------------
        # GESTION DES RÉPONSES API
        # -----------------------------
        if isinstance(resultat, list):
            st.success("Réponse du tuteur")
            st.write(resultat[0]["generated_text"])

        elif isinstance(resultat, dict) and "error" in resultat:
            st.error(f"{resultat['error']}")

        else:
            st.error("Réponse inattendue du modèle.")
