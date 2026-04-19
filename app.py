import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from google import genai
import datetime

# ─── CONFIGURAÇÃO MOBILE-FIRST ────────────────────────────────
st.set_page_config(page_title="OPERAÇÃO RESGATE", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS PARA MATAR AS "BARRIGAS" E MELHORAR O VISUAL ─────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; }
    /* Ajusta as tabelas para não criarem barras desnecessárias */
    .stDataFrame { width: 100% !important; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: #1e2130; border-radius: 5px; padding: 5px 10px; color: #888; font-size: 12px;
    }
    .stTabs [aria-selected="true"] { background: #1F3864 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ─── CONEXÃO ──────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

# ─── CABEÇALHO RÁPIDO ─────────────────────────────────────────
hoje = datetime.date.today()
dia_semana = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"][hoje.weekday()]
st.subheader(f"⚡ {dia_semana}, {hoje.strftime('%d/%m')}")

# ─── ABAS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Home", "📚 Estudo", "💪 Treino", "🎓 Notas", "🤖 IA"])

def carregar_aba(nome_aba):
    try:
        return conn.read(worksheet=nome_aba)
    except:
        st.error(f"⚠️ Aba '{nome_aba}' não encontrada!")
        return None

# --- ABA 1: HOME ---
with tab1:
    df_home = carregar_aba("📋 Visão Geral")
    if df_home is not None:
        st.dataframe(df_home, width="stretch", hide_index=True)

# --- ABA 2: ESTUDOS (COM SALVAMENTO) ---
with tab2:
    st.write("📝 **Sessões de Hoje**")
    df_est = carregar_aba("📚 Registro de Estudos")
    if df_est is not None:
        df_edit_est = st.data_editor(df_est, num_rows="dynamic", width="stretch", hide_index=True)
        if st.button("💾 Salvar Estudos", use_container_width=True):
            conn.update(worksheet="📚 Registro de Estudos", data=df_edit_est)
            st.success("✅ Sincronizado!")

# --- ABA 3: TREINO ---
with tab3:
    df_tr = carregar_aba("💪 Treino")
    if df_tr is not None:
        df_edit_tr = st.data_editor(df_tr, num_rows="dynamic", width="stretch", hide_index=True)
        if st.button("💾 Salvar Cargas", use_container_width=True):
            conn.update(worksheet="💪 Treino", data=df_edit_tr)
            st.success("💪 Treino Atualizado!")

# --- ABA 4: NOTAS ---
with tab4:
    df_nt = carregar_aba("🎓 Notas Acadêmicas")
    if df_nt is not None:
        df_edit_nt = st.data_editor(df_nt, num_rows="dynamic", width="stretch", hide_index=True)
        if st.button("💾 Salvar Notas", use_container_width=True):
            conn.update(worksheet="🎓 Notas Acadêmicas", data=df_edit_nt)
            st.balloons()

# --- ABA 5: TUTOR IA (GEMINI) ---
with tab5:
    st.write("🤖 **Tutor de Engenharia**")
    key = st.secrets.get("GEMINI_API_KEY")
    if key:
        try:
            client = genai.Client(api_key=key)
            if "chat" not in st.session_state: st.session_state.chat = []
            
            for m in st.session_state.chat:
                with st.chat_message(m["role"]): st.markdown(m["content"])

            if p := st.chat_input("Dúvida de Cálculo ou Química?"):
                st.session_state.chat.append({"role": "user", "content": p})
                with st.chat_message("user"): st.markdown(p)
                
                with st.chat_message("assistant"):
                    ctx = "Jonathan, aluno de Civil na UENF. Foque em Álgebra Linear e Química."
                    r = client.models.generate_content(model="gemini-2.0-flash", contents=f"{ctx}\n\n{p}")
                    st.markdown(r.text)
                    st.session_state.chat.append({"role": "assistant", "content": r.text})
        except Exception as e:
            st.error(f"Erro na IA: {e}")
