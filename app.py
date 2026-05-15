import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection  # <--- NUOVA LIBRERIA

# Configurazione Pagina
st.set_page_config(page_title="Mappa Metamoderna", page_icon="🎨", layout="wide")

custom_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-baseweb="slider"] { padding-top: 15px !important; padding-bottom: 15px !important; }
    .stNumberInput input { text-align: center; font-weight: bold; font-size: 1.1rem; }
    div[data-testid="stForm"] { border-radius: 15px; border: 1px solid rgba(250, 250, 250, 0.2); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ----------------- NUOVO DATABASE GOOGLE SHEETS -----------------
# Sostituisci questo con il VERO link del tuo foglio Google dello Step 1
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/IL_TUO_LINK_LUNGHISSIMO/edit#gid=0"

# Crea la connessione con i Segreti che hai salvato su Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Legge i dati da Google Sheets
        df = conn.read(spreadsheet=SPREADSHEET_URL, usecols=[0,1,2,3,4,5])
        # Se il foglio è totalmente vuoto, crea le colonne
        if df.empty or df.isna().all().all():
            return pd.DataFrame(columns=["nome", "tipo", "ironia", "post_ironia", "sincerita", "voti"])
        return df
    except Exception as e:
        return pd.DataFrame(columns=["nome", "tipo", "ironia", "post_ironia", "sincerita", "voti"])

def save_data(df):
    # Aggiorna il foglio Google con il nuovo dataframe
    conn.update(spreadsheet=SPREADSHEET_URL, data=df)

# Inizializzazione dati
df = load_data()
# -----------------------------------------------------------------


st.title("🎨 Mappa Culturale Ternaria")
st.markdown("Inserisci i tuoi contenuti preferiti e posizionali nel triangolo tra **Ironia**, **Post-Ironia** e **Sincerità**.")

# Layout a due colonne
col1, col2 = st.columns([1, 2], gap="large")

# Variabili per gestire il click sulla mappa
selected_nome = ""
selected_tipo = "Film"

# Disegniamo PRIMA la mappa (col2) per catturare il click dell'utente
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
            size_max=22,
            labels={"ironia": "Ironia", "post_ironia": "Post-Ironia", "sincerita": "Sincerità"}
        )
        
        fig.update_traces(
            marker=dict(
                line=dict(width=2, color='DarkSlateGrey'),
                opacity=0.9
            )
        )
        
       # 1. Nomi agli angoli evidenziati (sintassi corretta per le nuove versioni di Plotly)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            ternary=dict(
                sum=100,
                bgcolor="rgba(0,0,0,0)",
                aaxis=dict(
                    title=dict(text="<b>IRONIA</b>", font=dict(size=18, color="#ff4b4b")), 
                    min=0, showgrid=False, showline=True, linewidth=2, linecolor='gray'
                ),
                baxis=dict(
                    title=dict(text="<b>POST-IRONIA</b>", font=dict(size=18, color="#4b4bff")), 
                    min=0, showgrid=False, showline=True, linewidth=2, linecolor='gray'
                ),
                caxis=dict(
                    title=dict(text="<b>SINCERITÀ</b>", font=dict(size=18, color="#4bff4b")), 
                    min=0, showgrid=False, showline=True, linewidth=2, linecolor='gray'
                ),
            ),
            height=650,
            margin=dict(l=40, r=40, t=60, b=40) 
        )
        
        # 3. Rendiamo la mappa cliccabile catturando l'evento di selezione
        event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points", key="mappa_ternaria")
        
        # Estraiamo il nome del punto cliccato
        if event and event.get("selection") and event["selection"].get("points"):
            selected_nome = event["selection"]["points"][0].get("hovertext", "")
            if selected_nome:
                # Troviamo la categoria associata per pre-compilarla
                match = df[df["nome"] == selected_nome]
                if not match.empty:
                    selected_tipo = match.iloc[0]["tipo"]
        
        with st.expander("📄 Visualizza Tabella Dati Completa"):
            st.dataframe(df.sort_values(by="voti", ascending=False), use_container_width=True)
    else:
        st.info("👈 Nessun dato presente. Inizia aggiungendo un contenuto nel pannello di sinistra.")

# Disegniamo DOPO il modulo (col1) così può usare i dati del click
with col1:
    st.subheader("➕ Aggiungi o Vota")
    
    if selected_nome:
        st.info(f"📍 Hai cliccato su **{selected_nome}**. Inserisci il tuo voto per aggiornare la media.")
    else:
        st.markdown("Clicca un punto sulla mappa per votarlo, oppure compila i campi per un **nuovo inserimento**.")
    
    with st.form("add_form", clear_on_submit=False):
        # I campi si riempiono automaticamente se selected_nome non è vuoto
        nuovo_nome = st.text_input("Nome (es. Matrix, The Office...)", value=selected_nome).strip()
        
        options = ["Film", "Libro", "Serie TV", "Videogioco", "Altro"]
        idx_tipo = options.index(selected_tipo) if selected_tipo in options else 0
        tipo = st.selectbox("Categoria", options, index=idx_tipo)
        
        st.write("Distribuisci **esattamente 100 punti**:")
        # 4. I valori di default sono impostati a 0
        v_ironia = st.number_input("Ironia", min_value=0, max_value=100, value=0, step=1)
        v_post_ironia = st.number_input("Post-Ironia", min_value=0, max_value=100, value=0, step=1)
        v_sincerita = st.number_input("Sincerità", min_value=0, max_value=100, value=0, step=1)
        
        submitted = st.form_submit_button("Registra Voto", use_container_width=True)
        
        if submitted:
            totale = v_ironia + v_post_ironia + v_sincerita
            
            if nuovo_nome == "":
                st.error("Inserisci un nome valido!")
            # 2. Errore bloccante se la somma non fa 100
            elif totale != 100:
                st.error(f"❌ Errore: La somma delle tre caratteristiche deve essere esattamente 100! Hai inserito {totale}.")
            else:
                # I voti inseriti sono già percentuali corrette perché la somma è 100
                n_i = v_ironia
                n_p = v_post_ironia
                n_s = v_sincerita
                
                nome_esiste = df["nome"].str.lower() == nuovo_nome.lower()
                
                if nome_esiste.any():
                    idx = df[nome_esiste].index[0]
                    n_voti = df.at[idx, "voti"]
                    
                    df.at[idx, "ironia"] = ((df.at[idx, "ironia"] * n_voti) + n_i) / (n_voti + 1)
                    df.at[idx, "post_ironia"] = ((df.at[idx, "post_ironia"] * n_voti) + n_p) / (n_voti + 1)
                    df.at[idx, "sincerita"] = ((df.at[idx, "sincerita"] * n_voti) + n_s) / (n_voti + 1)
                    df.at[idx, "voti"] = n_voti + 1
                    
                    nome_reale = df.at[idx, "nome"]
                    st.success(f"✅ Voto registrato per '{nome_reale}'. La media è stata aggiornata.")
                else:
                    new_row = {"nome": nuovo_nome, "tipo": tipo, "ironia": n_i, "post_ironia": n_p, "sincerita": n_s, "voti": 1}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"🎉 '{nuovo_nome}' aggiunto per la prima volta!")
                
                save_data(df)
                st.rerun()