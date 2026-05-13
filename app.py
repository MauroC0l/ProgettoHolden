import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurazione Pagina
st.set_page_config(page_title="Mappa Metamoderna", page_icon="🎨", layout="wide")

# 4. Grafica elegante e moderna (CSS personalizzato)
custom_css = """
<style>
    /* Nasconde il menu di Streamlit per un look più pulito come una vera web app */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Rende gli slider e gli input più spessi e moderni */
    div[data-baseweb="slider"] {
        padding-top: 15px !important;
        padding-bottom: 15px !important;
    }
    .stNumberInput input {
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* Arrotonda i bordi dei form */
    div[data-testid="stForm"] {
        border-radius: 15px;
        border: 1px solid rgba(250, 250, 250, 0.2);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# File del database
DB_FILE = "data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["nome", "tipo", "ironia", "post_ironia", "sincerita", "voti"])
    else:
        return pd.DataFrame(columns=["nome", "tipo", "ironia", "post_ironia", "sincerita", "voti"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# Inizializzazione dati
df = load_data()

st.title("🎨 Mappa Culturale Ternaria")
st.markdown("Inserisci i tuoi contenuti preferiti e posizionali nel triangolo tra **Ironia**, **Post-Ironia** e **Sincerità**.")

# Layout a due colonne
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("➕ Aggiungi o Vota un oggetto")
    st.markdown("Se inserisci un nome già esistente, il tuo voto verrà **unito** a quello precedente.")
    
    with st.form("add_form", clear_on_submit=True):
        nuovo_nome = st.text_input("Nome (es. Matrix, The Office...)").strip()
        tipo = st.selectbox("Categoria", ["Film", "Libro", "Serie TV", "Videogioco", "Altro"])
        
        st.write("Distribuisci i punteggi (puoi digitare o usare i tasti):")
        # 3. Input migliorati: permettono inserimento manuale da tastiera e sono più larghi
        v_ironia = st.number_input("Ironia", min_value=0, max_value=100, value=33, step=1)
        v_post_ironia = st.number_input("Post-Ironia", min_value=0, max_value=100, value=33, step=1)
        v_sincerita = st.number_input("Sincerità", min_value=0, max_value=100, value=34, step=1)
        
        submitted = st.form_submit_button("Inserisci nella mappa", use_container_width=True)
        
        if submitted:
            if nuovo_nome == "":
                st.error("Inserisci un nome valido!")
            else:
                totale = v_ironia + v_post_ironia + v_sincerita
                if totale == 0:
                    st.error("Il totale non può essere zero.")
                else:
                    # Normalizzazione
                    n_i = (v_ironia / totale) * 100
                    n_p = (v_post_ironia / totale) * 100
                    n_s = (v_sincerita / totale) * 100
                    
                    # 5. Logica Anti-Duplicato
                    # Controlla se il nome esiste già (ignorando maiuscole/minuscole)
                    nome_esiste = df["nome"].str.lower() == nuovo_nome.lower()
                    
                    if nome_esiste.any():
                        # Aggiorna elemento esistente
                        idx = df[nome_esiste].index[0]
                        n_voti = df.at[idx, "voti"]
                        
                        df.at[idx, "ironia"] = ((df.at[idx, "ironia"] * n_voti) + n_i) / (n_voti + 1)
                        df.at[idx, "post_ironia"] = ((df.at[idx, "post_ironia"] * n_voti) + n_p) / (n_voti + 1)
                        df.at[idx, "sincerita"] = ((df.at[idx, "sincerita"] * n_voti) + n_s) / (n_voti + 1)
                        df.at[idx, "voti"] = n_voti + 1
                        
                        # Ripristina la maiuscola corretta usata in precedenza per bellezza
                        nome_reale = df.at[idx, "nome"]
                        st.success(f"✅ '{nome_reale}' esisteva già! Ho aggiornato la media con il tuo voto.")
                    else:
                        # Crea nuovo elemento
                        new_row = {"nome": nuovo_nome, "tipo": tipo, "ironia": n_i, "post_ironia": n_p, "sincerita": n_s, "voti": 1}
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        st.success(f"🎉 '{nuovo_nome}' aggiunto per la prima volta!")
                    
                    save_data(df)
                    st.rerun()

with col2:
    st.subheader("📊 La Mappa")
    if not df.empty:
        fig = px.scatter_ternary(
            df, 
            a="ironia", 
            b="post_ironia", 
            c="sincerita", 
            hover_name="nome", 
            color="tipo",
            size="voti",
            size_max=22, # Pallini un po' più grandi
            labels={"ironia": "Ironia", "post_ironia": "Post-Ironia", "sincerita": "Sincerità"}
        )
        
        # 1. e 2. Triangolo pulito e pallini sopra
        fig.update_traces(
            marker=dict(
                line=dict(width=2, color='DarkSlateGrey'), # Bordo scuro sui pallini per staccarli dallo sfondo
                opacity=0.9
            )
        )
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", # Sfondo trasparente
            plot_bgcolor="rgba(0,0,0,0)",
            ternary=dict(
                sum=100,
                bgcolor="rgba(0,0,0,0)", # Rimuove lo sfondo interno del triangolo
                aaxis=dict(title="Ironia", min=0, showgrid=False, showline=True, linewidth=2, linecolor='gray'),
                baxis=dict(title="Post-Ironia", min=0, showgrid=False, showline=True, linewidth=2, linecolor='gray'),
                caxis=dict(title="Sincerità", min=0, showgrid=False, showline=True, linewidth=2, linecolor='gray'),
            ),
            height=650,
            margin=dict(l=20, r=20, t=40, b=20) # Margini ottimizzati
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📄 Visualizza Tabella Dati Completa"):
            st.dataframe(df.sort_values(by="voti", ascending=False), use_container_width=True)
    else:
        st.info("👈 Nessun dato presente. Inizia aggiungendo un contenuto nel pannello di sinistra.")