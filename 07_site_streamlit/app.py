"""
Priorisation des rénovations énergétiques DPE — Île-de-France
Version web interactive (Streamlit) du dashboard Power BI.

Pour lancer en local :
    pip install -r requirements.txt
    streamlit run app.py

La donnée attendue est un export CSV de la vue SQL `vue_priorite_renovation`
(mêmes colonnes que le dashboard Power BI), placé à côté de ce fichier sous
le nom `vue_priorite_renovation.csv`.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------
# Configuration générale + thème bleu uni (cohérent avec Power BI)
# -----------------------------------------------------------------

st.set_page_config(
    page_title="Priorisation des rénovations DPE — IDF",
    page_icon="🏠",
    layout="wide",
)

BLEU_FONCE = "#1A237E"
BLEU_MOYEN = "#3949AB"
BLEU_CLAIR = "#7986CB"
FOND = "#F4F6FB"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {FOND}; }}
    div[data-testid="stMetric"] {{
        background-color: {BLEU_FONCE};
        border-radius: 10px;
        padding: 16px;
    }}
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div {{
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Centroïdes approximatifs des départements d'Île-de-France (pour la carte)
CENTROIDES_DEPARTEMENTS = {
    "75": (48.8566, 2.3522),
    "77": (48.8499, 2.9350),
    "78": (48.8014, 1.9761),
    "91": (48.6300, 2.4400),
    "92": (48.8924, 2.2154),
    "93": (48.9362, 2.3574),
    "94": (48.7900, 2.4550),
    "95": (49.0500, 2.1200),
}

# -----------------------------------------------------------------
# Chargement des données
# -----------------------------------------------------------------

@st.cache_data
def charger_donnees():
    df = pd.read_csv("vue_priorite_renovation")
    # Sécurité : uniformise les noms de colonnes attendus
    df.columns = [c.strip() for c in df.columns]
    df["code_departement_ban"] = df["code_departement_ban"].astype(str).str.zfill(2)
    return df

try:
    df = charger_donnees()
except FileNotFoundError:
    st.error(
        "Fichier `vue_priorite_renovation.csv` introuvable. "
        "Exporte la vue SQL en CSV et place le fichier à côté de app.py."
    )
    st.stop()

# -----------------------------------------------------------------
# Filtres (équivalent des segments Power BI)
# -----------------------------------------------------------------

st.sidebar.header("Filtres")

etiquettes = sorted(df["etiquette_dpe"].dropna().unique().tolist())
etiquettes_choisies = st.sidebar.multiselect(
    "Étiquette DPE", options=etiquettes, default=etiquettes
)

departements = sorted(df["code_departement_ban"].dropna().unique().tolist())
departements_choisis = st.sidebar.multiselect(
    "Département", options=departements, default=departements
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Liens**
    📂 [Code source & pipeline SQL sur GitHub](https://github.com/ben-enfaneassoumani/priorisation-renovations-dpe-idf)
    💼 [Profil LinkedIn](https://linkedin.com/in/ben-enfaneassoumani)
    """
)

df_filtre = df[
    df["etiquette_dpe"].isin(etiquettes_choisies)
    & df["code_departement_ban"].isin(departements_choisis)
]

if df_filtre.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# -----------------------------------------------------------------
# Titre
# -----------------------------------------------------------------

st.markdown(
    f"""
    <div style="background-color:{BLEU_FONCE}; padding:24px; border-radius:10px; margin-bottom:20px;">
        <h1 style="color:white; margin:0;">Priorisation des rénovations DPE — IDF</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("📖 Contexte du projet", expanded=True):
    st.markdown(
        """
        Depuis janvier 2025, un bailleur qui possède un logement classé **G**
        au DPE n'a plus la possibilité de le proposer à la location. Il en
        ira de même pour les logements classés **F** à partir de 2028 (loi
        Climat et Résilience). Avec un budget de rénovation forcément limité
        face à des milliers de logements concernés, cet outil calcule un
        **score de priorité** par logement — combinant rentabilité (gain
        locatif et écologique rapporté au coût des travaux) et urgence
        réglementaire — pour identifier lesquels rénover en premier.

        Les hypothèses de calcul (coût au m² par étiquette, loyer de
        référence, budget disponible) sont des ordres de grandeur assumés et
        documentés en détail dans le
        [README du dépôt GitHub](https://github.com/ben-enfaneassoumani/priorisation-renovations-dpe-idf),
        avec le pipeline SQL complet (nettoyage, dédoublonnage, vue métier)
        et le fichier Power BI source.
        """
    )

# -----------------------------------------------------------------
# KPI (cartes)
# -----------------------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Logements à rénover", f"{df_filtre['numero_dpe'].count():,}".replace(",", " "))
col2.metric("Budget total estimé", f"{df_filtre['cout_travaux'].sum() / 1e6:.2f} M€")
col3.metric("Gain locatif annuel", f"{df_filtre['gain_financier'].sum() / 1e6:.2f} M€")
col4.metric("Gain écologique", f"{df_filtre['gain_ecologique_euros'].sum() / 1e6:.2f} M€")
col5.metric("Score de priorité moyen", f"{df_filtre['score_priorite'].mean():.2f}")

st.write("")

# -----------------------------------------------------------------
# Histogramme — Nombre de logements F/G par département
# -----------------------------------------------------------------

st.subheader("Nombre de logements F/G par département")

df_hist = (
    df_filtre.groupby(["code_departement_ban", "etiquette_dpe"])["numero_dpe"]
    .count()
    .reset_index(name="nombre_logements")
)

fig_hist = px.bar(
    df_hist,
    x="code_departement_ban",
    y="nombre_logements",
    color="etiquette_dpe",
    barmode="group",
    color_discrete_map={"F": BLEU_CLAIR, "G": BLEU_FONCE},
    labels={
        "code_departement_ban": "Département",
        "nombre_logements": "Nombre de logements",
        "etiquette_dpe": "Étiquette",
    },
)
fig_hist.update_layout(plot_bgcolor="white", paper_bgcolor="white")
st.plotly_chart(fig_hist, use_container_width=True)

# -----------------------------------------------------------------
# Tableau + carte, côte à côte
# -----------------------------------------------------------------

col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.subheader("Rénovations prioritaires — IDF")

    critere_tri = st.selectbox(
        "Trier le tableau par",
        options=["score_priorite", "gain_financier", "cout_travaux"],
        format_func=lambda x: {
            "score_priorite": "Score de priorité",
            "gain_financier": "Gain locatif annuel",
            "cout_travaux": "Coût des travaux",
        }[x],
    )

    df_table = (
        df_filtre.groupby(["nom_commune_ban", "code_postal_ban", "etiquette_dpe"])
        .agg(
            score_priorite=("score_priorite", "mean"),
            cout_travaux=("cout_travaux", "sum"),
            gain_financier=("gain_financier", "sum"),
        )
        .reset_index()
        .sort_values(critere_tri, ascending=False)
        .head(50)
    )

    st.dataframe(
        df_table.style.format(
            {
                "score_priorite": "{:.2f}",
                "cout_travaux": "{:,.0f} €",
                "gain_financier": "{:,.0f} €",
            }
        ),
        use_container_width=True,
        height=420,
    )

with col_droite:
    st.subheader("Répartition géographique des rénovations")

    df_carte = (
        df_filtre.groupby(["code_departement_ban", "etiquette_dpe"])["numero_dpe"]
        .count()
        .reset_index(name="nombre_logements")
    )
    df_carte["lat"] = df_carte["code_departement_ban"].map(
        lambda d: CENTROIDES_DEPARTEMENTS.get(d, (None, None))[0]
    )
    df_carte["lon"] = df_carte["code_departement_ban"].map(
        lambda d: CENTROIDES_DEPARTEMENTS.get(d, (None, None))[1]
    )
    df_carte = df_carte.dropna(subset=["lat", "lon"])

    fig_carte = px.scatter_mapbox(
        df_carte,
        lat="lat",
        lon="lon",
        size="nombre_logements",
        color="etiquette_dpe",
        color_discrete_map={"F": BLEU_CLAIR, "G": BLEU_FONCE},
        hover_name="code_departement_ban",
        size_max=45,
        zoom=7.2,
        mapbox_style="open-street-map",
    )
    fig_carte.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=420)
    st.plotly_chart(fig_carte, use_container_width=True)

st.caption(
    "Carte agrégée au niveau département (centroïdes approximatifs) — "
    "granularité plus fine possible avec un géocodage complet des codes postaux."
)

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; font-size:13px; color:#5C6BC0;">
        Ben-Enfane Assoumani — Master 1 Statistique et Sciences des Données, Université de Montpellier<br>
        <a href="https://github.com/ben-enfaneassoumani/priorisation-renovations-dpe-idf" style="color:#1A237E;">Code source & pipeline SQL sur GitHub</a>
        &nbsp;·&nbsp;
        <a href="https://linkedin.com/in/ben-enfaneassoumani" style="color:#1A237E;">LinkedIn</a>
    </div>
    """,
    unsafe_allow_html=True,
)
