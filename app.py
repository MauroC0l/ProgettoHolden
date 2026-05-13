import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurazione Pagina
st.set_page_config(page_title="Mappa Metamoderna", layout="wide")

# File del database
DB_FILE = "data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["nome", "tipo", "ironia", "post_ironia", "sincerita", "voti"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# Inizializzazione dati
df = load_data()

st.title("🎨 Mappa Culturale Ternaria")
st.markdown("Inserisci i tuoi contenuti preferiti e posizionali nel triangolo tra **Ironia**, **Post-Ironia** e **Sincerità**.")

# Layout a due colonne: Input e Voto a sinistra, Grafico a destra
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("➕ Aggiungi un nuovo oggetto")
    with st.form("add_form", clear_on_submit=True):
        nuovo_nome = st.text_input("Nome (Film, Libro, Serie...)")
        tipo = st.selectbox("Categoria", ["Film", "Libro", "Serie TV", "Altro"])
        
        st.write("Distribuisci 100 punti tra le caratteristiche:")
        v_ironia = st.slider("Ironia", 0, 100, 33)
        v_post_ironia = st.slider("Post-Ironia", 0, 100, 33)
        v_sincerita = st.slider("Sincerità", 0, 100, 34)
        
        submitted = st.form_submit_state = st.form_submit_button("Aggiungi alla mappa")
        
        if submitted:
            totale = v_ironia + v_post_ironia + v_sincerita
            # Normalizzazione per sicurezza (deve fare 100)
            n_i = (v_ironia / totale) * 100
            n_p = (v_post_ironia / totale) * 100
            n_s = (v_sincerita / totale) * 100
            
            new_row = {"nome": nuovo_nome, "tipo": tipo, "ironia": n_i, "post_ironia": n_p, "sincerita": n_s, "voti": 1}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"{nuovo_nome} aggiunto!")
            st.rerun()

    st.divider()

    st.subheader("🗳️ Vota un oggetto esistente")
    if not df.empty:
        oggetto_da_votare = st.selectbox("Scegli cosa votare", df["nome"].unique())
        with st.form("vote_form", clear_on_submit=True):
            vi_v = st.slider("Ironia", 0, 100, 33, key="vi")
            vp_v = st.slider("Post-Ironia", 0, 100, 33, key="vp")
            vs_v = st.slider("Sincerità", 0, 100, 34, key="vs")
            
            voted = st.form_submit_button("Invia Voto")
            
            if voted:
                idx = df[df["nome"] == oggetto_da_votare].index[0]
                n_voti = df.at[idx, "voti"]
                
                # Calcolo nuova media pesata
                tot_v = vi_v + vp_v + vs_v
                df.at[idx, "ironia"] = ((df.at[idx, "ironia"] * n_voti) + (vi_v/tot_v*100)) / (n_voti + 1)
                df.at[idx, "post_ironia"] = ((df.at[idx, "post_ironia"] * n_voti) + (vp_v/tot_v*100)) / (n_voti + 1)
                df.at[idx, "sincerita"] = ((df.at[idx, "sincerita"] * n_voti) + (vs_v/tot_v*100)) / (n_voti + 1)
                df.at[idx, "voti"] = n_voti + 1
                
                save_data(df)
                st.success("Voto registrato!")
                st.rerun()
    else:
        st.info("Aggiungi prima un oggetto per poter votare.")

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
            size="voti", # Più voti ha, più il pallino è grande
            size_max=15,
            labels={"ironia": "Ironia", "post_ironia": "Post-Ironia", "sincerita": "Sincerità"}
        )
        
        fig.update_layout(
            ternary=dict(
                sum=100,
                aaxis=dict(title="Ironia", min=0),
                baxis=dict(title="Post-Ironia", min=0),
                caxis=dict(title="Sincerità", min=0),
            ),
            height=700
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("### Tabella Riepilogativa")
        st.dataframe(df[["nome", "tipo", "voti"]].sort_values(by="voti", ascending=False))
    else:
        st.warning("Nessun dato presente. Inizia aggiungendo un contenuto a sinistra.")