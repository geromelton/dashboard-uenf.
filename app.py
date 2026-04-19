import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from google import genai
import datetime

# ─── CONFIGURAÇÃO MOBILE ──────────────────────────────────────
st.set_page_config(page_title="OPERAÇÃO RESGATE", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS PARA ELIMINAR BARRIGAS E ESPAÇOS ─────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    /* Estilo das Abas para Celular */
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        background: #1e2130; border-radius: 4px; padding: 4px 8px; color: #888; font-size: 11px;
    }
    .stTabs [aria-selected="true"] { background: #1F3864 !important; color: white !important; }
    /* Tira margens bobas que criam 'barrigas' */
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
</style>
""", unsafe_allow_html=True)

# ─── CONEXÃO ──────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

# ─── CABEÇALHO ────────────────────────────────────────────────
hoje = datetime.date.today()
st.subheader(f"⚡ Domingo, {hoje.strftime('%d/%m')}")

# ─── ABAS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📚 Estudo", "💪 Treino", "🎓 Notas", "🤖 IA"])

# Função para ler a aba limpando o índice (evita o erro do seu log)
def carregar_dados(nome):
    try:
        df = conn.read(worksheet=nome)
        return df.reset_index(drop=True)
    except:
        return None

# --- ABA 1: HOME ---
with tab1:
    df_h = carregar_dados("📋 Visão Geral")
    if df_h is not None:
        st.dataframe(df_h, width=1000, hide_index=True)

# --- ABA 2: ESTUDOS ---
with tab2:
    st.write("📖 **Foco: Cálculo e Química**")
    df_e = carregar_dados("📚 Registro de Estudos")
    if df_e is not None:
        df_edit_e = st.data_editor(df_e, num_rows="dynamic", width=1000)
        if st.button("💾 Salvar Estudos", use_container_width=True):
            conn.update(worksheet="📚 Registro de Estudos", data=df_edit_e)
            st.success("Sincronizado!")

# --- ABA 3: TREINO ---
with tab3:
    st.write("💪 **Black House Gym**")
    df_t = carregar_dados("💪 Treino")
    if df_t is not None:
        df_edit_t = st.data_editor(df_t, num_rows="dynamic", width=1000)
        if st.button("💾 Salvar Cargas", use_container_width=True):
            conn.update(worksheet="💪 Treino", data=df_edit_t)

# --- ABA 4: NOTAS ---
with tab4:
    st.write("🎓 **Recuperar P1!**")
    df_n = carregar_dados("🎓 Notas Acadêmicas")
    if df_n is not None:
        df_edit_n = st.data_editor(df_n, num_rows="dynamic", width=1000)
        if st.button("💾 Salvar Notas", use_container_width=True):
            conn.update(worksheet="🎓 Notas Acadêmicas", data=df_edit_n)

# --- ABA 5: IA (GEMINI) ---
with tab5:
    st.write("🤖 **Tutor de Engenharia UENF**")
    key = st.secrets.get("GEMINI_API_KEY")
    
    if key:
        # Mostra um aviso se não houver conversa ainda, para não parecer vazio
        if "chat" not in st.session_state:
            st.session_state.chat = []
            st.info("O Gemini está online. Digite sua dúvida no campo abaixo!")

        # Área das mensagens
        for m in st.session_state.chat:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        # O CAMPO DE ESCREVER (Ele fica no rodapé do celular)
        if prompt := st.chat_input("Dúvida de Álgebra ou Cálculo?"):
            st.session_state.chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    client = genai.Client(api_key=key)
                    ctx = "Jonathan, calouro de Civil na UENF. Ajude-o a estudar para as P2."
                    r = client.models.generate_content(model="gemini-2.0-flash", contents=f"{ctx}\n\n{prompt}")
                    st.markdown(r.text)
                    st.session_state.chat.append({"role": "assistant", "content": r.text})
                except Exception as e:
                    st.error(f"Erro: {e}")
    else:
        st.error("Chave API não configurada nos Secrets.")
