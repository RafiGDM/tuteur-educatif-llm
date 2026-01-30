import streamlit as st
import requests
import os

# -----------------------------
# CONFIGURATION DE LA PAGE
# -----------------------------
st.set_page_config(
    page_title="Tuteur Éducatif Personnalisé (LLM)",
    page_icon="🎓",
    layout="centered"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        border: none;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Tuteur Éducatif Personnalisé")
st.markdown("""
### Bienvenue dans votre assistant pédagogique intelligent
Ce tuteur utilise un **Large Language Model (LLM)** pour accompagner 
les étudiants de **Licence 3 Informatique** de manière personnalisée.
""")

# -----------------------------
# SIDEBAR POUR LES INFORMATIONS
# -----------------------------
with st.sidebar:
    st.header("ℹ️ Informations")
    st.write("""
    **Fonctionnalités :**
    - Adaptation au niveau
    - Explications pédagogiques
    - Exemples concrets
    - Vérification de compréhension
    
    **Matières disponibles :**
    1. Programmation Python
    2. Algorithmique
    """)
    
    st.header("🔑 Configuration API")
    api_source = st.radio(
        "Source de l'API :",
        ["Hugging Face", "OpenAI (à venir)"]
    )
    
    if api_source == "Hugging Face":
        st.info("Utilise l'API Hugging Face avec Mistral 7B")
    else:
        st.warning("Option en développement")

# -----------------------------
# PARAMÈTRES UTILISATEUR
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    matiere = st.selectbox(
        "📘 Choisissez la matière :",
        ["Programmation Python", "Algorithmique et structures de données"],
        help="Sélectionnez la matière que vous souhaitez étudier"
    )

with col2:
    niveau = st.selectbox(
        "🎯 Choisissez votre niveau :",
        ["Débutant", "Intermédiaire", "Avancé"],
        help="Cela permet d'adapter le niveau d'explication"
    )

st.markdown("---")

question = st.text_area(
    "✏️ Posez votre question :",
    placeholder="Ex : Explique-moi les boucles en Python\nOu : Quelle est la différence entre une liste et un tuple ?",
    height=150
)

# -----------------------------
# CLÉ API HUGGING FACE
# -----------------------------
# Pour Vercel, utilisez les variables d'environnement
HF_API_TOKEN = st.secrets.get("HF_API_TOKEN", os.getenv("HF_API_TOKEN"))

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
} if HF_API_TOKEN else {}

# -----------------------------
# FONCTION D'APPEL AU LLM AMÉLIORÉE
# -----------------------------
def appeler_llm(prompt):
    try:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 800,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            },
            "options": {
                "use_cache": True,
                "wait_for_model": True
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 503:
            return {"error": "Le modèle est en cours de chargement, veuillez réessayer dans 30 secondes"}
        else:
            return {"error": f"Erreur API: {response.status_code}"}
            
    except requests.exceptions.Timeout:
        return {"error": "Timeout - Le serveur met trop de temps à répondre"}
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

# -----------------------------
# BOUTON DE GÉNÉRATION
# -----------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generer = st.button("📤 Obtenir l'explication", use_container_width=True)

if generer:
    if not HF_API_TOKEN:
        st.error("""
        ❌ Clé API Hugging Face manquante.
        
        **Pour tester localement :**
        1. Créez un fichier `.streamlit/secrets.toml`
        2. Ajoutez : `HF_API_TOKEN = "votre_token_ici"`
        3. Ou définissez la variable d'environnement
        
        **Pour Vercel :**
        1. Allez dans Project Settings > Environment Variables
        2. Ajoutez HF_API_TOKEN avec votre token
        """)
    elif question.strip() == "":
        st.warning("⚠️ Veuillez entrer une question.")
    else:
        with st.spinner("⏳ Le tuteur réfléchit à la meilleure explication pour vous..."):
            # Construction du prompt pédagogique
            prompt = f"""
Tu es un tuteur universitaire expert en informatique. Tu réponds à un étudiant de Licence 3.

CONTEXTE:
- Matière: {matiere}
- Niveau de l'étudiant: {niveau}
- Question: {question}

INSTRUCTIONS PÉDAGOGIQUES:
1. ADAPTE ton langage au niveau ({niveau})
   - Débutant: termes simples, métaphores
   - Intermédiaire: concepts techniques avec explications
   - Avancé: détails techniques, bonnes pratiques

2. STRUCTURE ta réponse:
   a) Introduction claire du concept
   b) Explication progressive
   c) Exemple concret en code si applicable
   d) Points clés à retenir
   e) Question de vérification de compréhension

3. TON STYLE:
   - Encourageant et positif
   - Pédagogique mais pas condescendant
   - Précis techniquement
   - Utilise des analogies si utile

4. À LA FIN, pose UNE question simple pour vérifier que l'étudiant a compris.

COMMENCE TA RÉPONSE DIRECTEMENT:
"""

            resultat = appeler_llm(prompt)

        st.markdown("---")
        
        if isinstance(resultat, list):
            if "generated_text" in resultat[0]:
                st.success("✅ Réponse du tuteur")
                st.markdown("### 📝 Explication :")
                st.markdown(resultat[0]["generated_text"])
                
                # Section feedback
                st.markdown("---")
                st.subheader("📊 Évaluez cette réponse")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍 Compris"):
                        st.balloons()
                        st.success("Super ! Continuons d'apprendre.")
                with col2:
                    if st.button("🤔 Pas clair"):
                        st.info("Essayez de reformuler votre question plus simplement.")
                with col3:
                    if st.button("🔄 Nouvelle question"):
                        st.experimental_rerun()
            else:
                st.error("Format de réponse inattendu de l'API")
        elif isinstance(resultat, dict) and "error" in resultat:
            st.error(f"⚠️ {resultat['error']}")
            st.info("💡 Conseil : Essayez avec une question plus simple ou réessayez plus tard.")
        else:
            st.error("Réponse inattendue de l'API")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("""
🎓 **Tuteur Éducatif Personnalisé** - Projet LLM 
| Déployé sur Vercel | Licence 3 Informatique
""")