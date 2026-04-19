import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from google import genai
import datetime

# ─── CONFIGURAÇÃO MOBILE-FIRST ────────────────────────────────
st.set_page_config(page_title="OPERAÇÃO RESGATE", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS PARA MATAR AS BARRIGAS E FIXAR O CHAT ────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: #1e2130; border-radius: 5px; padding: 5px 10px; color: #888; font-size: 12px;
    }
    .stTabs [aria-selected="true"] { background: #1F3864 !important; color: white !important; }
    /* Forçar largura total para evitar barrigas */
    [data-testid="stDataFrame"] { width: 100% !important; }
    .block-container { padding-top: 1rem; padding-bottom: 10rem; }
</style>
""", unsafe_allow_html=True)

# ─── CONEXÃO ──────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

# ─── CABEÇALHO ────────────────────────────────────────────────
hoje = datetime.date.today()
st.subheader(f"⚡ Domingo, {hoje.strftime('%d/%m')}")

# ─── ABAS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📚 Estudo", "💪 Treino", "🎓 Notas", "🤖 IA"])

# Função segura para carregar as abas
def load(sheet_name):
    try:
        # Resetamos o index para evitar o erro de 'hide_index' do seu log
        return conn.read(worksheet=sheet_name).reset_index(drop=True)
    except Exception as e:
        st.warning(f"Aba '{sheet_name}' não carregou. Verifique o nome na planilha!")
        return None

# --- ABA 1: HOME ---
with tab1:
    df_home = load("📋 Visão Geral")
    if df_home is not None:
        st.dataframe(df_home, use_container_width=True, hide_index=True)

# --- ABA 2: ESTUDOS ---
with tab2:
    st.write("📖 **Foco: Recuperar P1**")
    df_est = load("📚 Registro de Estudos")
    if df_est is not None:
        df_ed = st.data_editor(df_est, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Salvar Estudos", use_container_width=True):
            conn.update(worksheet="📚 Registro de Estudos", data=df_ed)
            st.success("Sincronizado!")

# --- ABA 3: TREINO ---
with tab3:
    df_tr = load("💪 Treino")
    if df_tr is not None:
        df_ed_tr = st.data_editor(df_tr, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Salvar Cargas", use_container_width=True):
            conn.update(worksheet="💪 Treino", data=df_ed_tr)

# --- ABA 4: NOTAS ---
with tab4:
    df_nt = load("🎓 Notas Acadêmicas")
    if df_nt is not None:
        df_ed_nt = st.data_editor(df_nt, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Salvar Notas", use_container_width=True):
            conn.update(worksheet="🎓 Notas Acadêmicas", data=df_ed_nt)

# --- ABA 5: IA (GEMINI) ---
with tab5:
    st.write("🤖 **Tutor UENF — Jonathan Nunes**")
    
    # Pegamos a chave
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if "chat" not in st.session_state:
        st.session_state.chat = []

    # Mostra as mensagens
    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # O CAMPO DE ESCREVER (Sempre visível no rodapé agora!)
    prompt = st.chat_input("Pergunte sobre Escalonamento ou Química...")
    
    if prompt:
        if not api_key:
            st.error("Erro: A chave API ainda não foi configurada nos Secrets do Streamlit!")
        else:
            st.session_state.chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    client = genai.Client(api_key=api_key)
                    # Contexto focado no Jonathan para ajudar com as matérias da UENF
                    instrucoes = "Você é um tutor para o Jonathan, calouro de Civil na UENF. Ajude-o com Álgebra Linear e Química."
                    response = client.models.generate_content(
                        model="gemini-2.0-flash", 
                        contents=f"{instrucoes}\n\n{prompt}"
                    )
                    st.markdown(response.text)
                    st.session_state.chat.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Erro na IA: {e}")
