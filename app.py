import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import datetime

# ─── CONFIGURAÇÃO DA PÁGINA ──────────────────────────────────
st.set_page_config(
    page_title="Operação Resgate",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── ESTILIZAÇÃO (CSS) ────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #1e2130; border-radius: 8px;
        padding: 8px 18px; color: #ccc; font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #1F3864 !important; color: white !important;
    }
    h1, h2, h3 { color: #e8ecf4; }
</style>
""", unsafe_allow_html=True)

# ─── CONEXÃO COM O GOOGLE SHEETS ──────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

# ─── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ Operação Resgate")
    st.markdown("---")
    hoje = datetime.date.today()
    dia_semana = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"][hoje.weekday()]
    st.markdown(f"📅 **Hoje:** {hoje.strftime('%d/%m/%Y')} ({dia_semana})")
    st.success("✅ Banco de Dados Conectado")

# ─── ABAS DO DASHBOARD ────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Rotina", 
    "📚 Estudos", 
    "💪 Treino", 
    "🎓 Notas", 
    "🤖 Tutor IA"
])

# --- ABA 1: ROTINA SEMANAL ---
with tab1:
    st.title("📋 Minha Rotina")
    try:
        df_visao = conn.read(worksheet="📋 Visão Geral")
        st.dataframe(df_visao, use_container_width=True, hide_index=True)
    except:
        st.info("💡 Aqui aparecerá sua aba '📋 Visão Geral' da planilha.")

# --- ABA 2: ESTUDOS (CRUD) ---
with tab2:
    st.title("📚 Registro de Estudos")
    try:
        df_est = conn.read(worksheet="📚 Registro de Estudos")
        df_edit = st.data_editor(df_est, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Salvar Estudos", use_container_width=True):
            conn.update(worksheet="📚 Registro de Estudos", data=df_edit)
            st.success("✅ Atualizado no Google Sheets!")
    except:
        st.error("Aba de Estudos não encontrada ou vazia.")

# --- ABA 3: TREINO ---
with tab3:
    st.title("💪 Registro de Treino")
    try:
        df_t = conn.read(worksheet="💪 Treino")
        df_t_edit = st.data_editor(df_t, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Salvar Treino", use_container_width=True):
            conn.update(worksheet="💪 Treino", data=df_t_edit)
            st.success("✅ Treino atualizado!")
    except: 
        st.error("Aba de Treino não encontrada ou vazia.")

# --- ABA 4: NOTAS ---
with tab4:
    st.title("🎓 Notas Acadêmicas")
    try:
        df_n = conn.read(worksheet="🎓 Notas Acadêmicas")
        df_n_edit = st.data_editor(df_n, num_rows="dynamic", use_container_width=True)
        if st.button("💾 Salvar Notas", use_container_width=True):
            conn.update(worksheet="🎓 Notas Acadêmicas", data=df_n_edit)
            st.success("✅ Notas atualizadas!")
    except: 
        st.error("Aba de Notas não encontrada ou vazia.")

# --- ABA 5: TUTOR GEMINI ---
with tab5:
    st.title("🤖 Tutor Gemini")
    if "GEMINI_API_KEY" not in st.secrets:
        st.warning("⚠️ Adicione a GEMINI_API_KEY nos Secrets do Streamlit.")
    else:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prompt = st.chat_input("Qual a dúvida de hoje?")
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                response = model.generate_content(f"Você é um tutor para um estudante de Engenharia Civil. Ajude-o com: {prompt}")
                st.markdown(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
