import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. Configurazione della Pagina (Titolo e Layout)
st.set_page_config(
    page_title="Metamodern Plotter",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS Avanzato per un look "All'avanguardia"
st.markdown("""
<style>
    /* Sfondo e Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Effetto Glassmorphism per i contenitori */
    div[data-testid="stForm"], .stDataFrame, .stExpander {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px !important;
    }

    /* Animazione per i titoli */
    .main-title {
        font-size: 3rem !important;
        font-weight: 700;
        background: linear-gradient(90deg, #ff8c00, #ffb347, #ffcc00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    /* Pulsanti Moderni */
    .stButton>button {
        width: 100%;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #ff8c00, #ff4500) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        transition: 0.3s all !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
    }

    /* Nasconde elementi superflui */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Gestione Database (Google Sheets)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1w8UZ1FHzw8ENbRv_uFyeLYpGcjbvWR44fNGZycFPGTI/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Importante: ttl=0 forza l'app a leggere i dati reali ogni volta, risolvendo il tuo problema
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        if df.empty or df.isna().all().all():
            return pd.DataFrame(columns=["nome", "tipo", "ironia", "post_ironia", "sincerita", "voti"])
            
        # Converte i vecchi dati in centesimi in decimi in memoria se necessario
        for col in ["ironia", "post_ironia", "sincerita"]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        sums = df["ironia"] + df["post_ironia"] + df["sincerita"]
        mask = sums > 15
        if mask.any():
            df.loc[mask, "ironia"] = df.loc[mask, "ironia"] / 10
            df.loc[mask, "post_ironia"] = df.loc[mask, "post_ironia"] / 10
            df.loc[mask, "sincerita"] = df.loc[mask, "sincerita"] / 10
            
        return df
    except:
        return pd.DataFrame(columns=["nome", "tipo", "ironia", "post_ironia", "sincerita", "voti"])

def save_data(new_df):
    conn.update(spreadsheet=SPREADSHEET_URL, data=new_df)

# Caricamento iniziale
df = load_data()

# 4. Header
st.markdown('<p class="main-title">🎨 Metamodern Plotter</p>', unsafe_allow_html=True)
st.markdown("Visualizza l'anima dei media nel triangolo tra **Ironia**, **Post-Ironia** e **Sincerità**.")

# 5. Logica di Interazione
col1, col2 = st.columns([1, 3], gap="large")

# Variabili di stato per il click
selected_nome = ""
selected_tipo = "Film"

with col2:
    st.subheader("📊 Mappa Culturale")
    if not df.empty:
        # Creazione Grafico Ternario
        fig = px.scatter_ternary(
            df, a="ironia", b="post_ironia", c="sincerita",
            hover_name="nome", color="tipo", size="voti", size_max=25,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_dark"
        )
        
        fig.update_traces(marker=dict(line=dict(width=2, color='white'), opacity=0.8))
        
        fig.update_layout(
            height=700,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            ternary=dict(
                sum=10,
                aaxis=dict(
                    title=dict(text="<b>IRONIA</b>", font=dict(size=18, color="#ff8c00")), 
                    min=0, showgrid=False
                ),
                baxis=dict(
                    title=dict(text="<b>POST-IRONIA</b>", font=dict(size=18, color="#ffb347")), 
                    min=0, showgrid=False
                ),
                caxis=dict(
                    title=dict(text="<b>SINCERITÀ</b>", font=dict(size=18, color="#ffcc00")), 
                    min=0, showgrid=False
                ),
            ),
            margin=dict(l=50, r=50, t=50, b=50)
        )

        # Gestione Click
        event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points", key="mappa")
        
        if event and event.get("selection") and event["selection"].get("points"):
            selected_nome = event["selection"]["points"][0].get("hovertext", "")
            match = df[df["nome"] == selected_nome]
            if not match.empty:
                selected_tipo = match.iloc[0]["tipo"]

        with st.expander("📄 Archivio Dati"):
            st.dataframe(df.sort_values(by="voti", ascending=False), use_container_width=True)
    else:
        st.info("La mappa è ancora vuota. Aggiungi il primo contenuto!")

with col1:
    st.subheader("✏️ Contribuisci")
    with st.container():
        with st.form("vote_form", clear_on_submit=True):
            nome_input = st.text_input("Titolo dell'opera", value=selected_nome, placeholder="Es. Interstellar").strip()
            categorie = ["Film", "Libro", "Serie TV", "Videogioco", "Musica", "Podcast", "Social", "Programma TV", "Esperienza Culturale", "Meme", "Altro"]
            idx = categorie.index(selected_tipo) if selected_tipo in categorie else categorie.index("Altro")
            tipo_input = st.selectbox("Categoria", categorie, index=idx)
            
            st.write("---")
            st.markdown("**Bilanciamento (Somma = 10)**")
            v_i = st.number_input("Quota Ironia", min_value=0, max_value=10, value=0)
            v_p = st.number_input("Quota Post-Ironia", min_value=0, max_value=10, value=0)
            v_s = st.number_input("Quota Sincerità", min_value=0, max_value=10, value=0)
            
            submitted = st.form_submit_button("REGISTRA VOTO")

            if submitted:
                totale = v_i + v_p + v_s
                if not nome_input:
                    st.warning("Inserisci un nome!")
                elif totale != 10:
                    st.error(f"La somma deve essere 10! (Totale attuale: {totale})")
                else:
                    # Logica Aggiornamento/Inserimento
                    nome_esiste = df["nome"].str.lower() == nome_input.lower()
                    if nome_esiste.any():
                        idx = df[nome_esiste].index[0]
                        count = df.at[idx, "voti"]
                        df.at[idx, "ironia"] = ((df.at[idx, "ironia"] * count) + v_i) / (count + 1)
                        df.at[idx, "post_ironia"] = ((df.at[idx, "post_ironia"] * count) + v_p) / (count + 1)
                        df.at[idx, "sincerita"] = ((df.at[idx, "sincerita"] * count) + v_s) / (count + 1)
                        df.at[idx, "voti"] = count + 1
                    else:
                        new_row = pd.DataFrame([{"nome": nome_input, "tipo": tipo_input, "ironia": v_i, "post_ironia": v_p, "sincerita": v_s, "voti": 1}])
                        df = pd.concat([df, new_row], ignore_index=True)
                    
                    save_data(df)
                    st.balloons()
                    st.rerun()

st.markdown("---")
st.caption("Creato per il Progetto Holden • Dati salvati su Google Cloud")