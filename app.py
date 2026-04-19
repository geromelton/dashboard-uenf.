import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from google import genai # Biblioteca nova e atualizada
import datetime

# ─── CONFIGURAÇÃO ─────────────────────────────────────────────
st.set_page_config(
    page_title="Operação Resgate — Jonathan Faria",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── ESTILO VISUAL ───────────────────────────────────────────
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

# ─── CONEXÃO ──────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

# ─── ABAS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Rotina", "📚 Estudos", "💪 Treino", "🎓 Notas", "🤖 Tutor IA"
])

# --- ABA 2: ESTUDOS (EXEMPLO DE CRUD ATUALIZADO) ---
with tab2:
    st.title("📚 Registro de Estudos")
    try:
        df_est = conn.read(worksheet="📚 Registro de Estudos")
        # Atualizado de 'use_container_width' para 'width="stretch"' conforme o log pediu
        df_edit = st.data_editor(df_est, num_rows="dynamic", width="stretch")
        if st.button("💾 Salvar Estudos", width="stretch"):
            conn.update(worksheet="📚 Registro de Estudos", data=df_edit)
            st.success("✅ Sincronizado com o Google Sheets!")
    except:
        st.error("Erro ao carregar aba de estudos.")

# --- ABA 5: TUTOR GEMINI (SINTAXE NOVA) ---
with tab5:
    st.title("🤖 Tutor Gemini")
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.warning("⚠️ Chave 'GEMINI_API_KEY' não encontrada nos Secrets.")
    else:
        try:
            # Nova forma de conectar com o Gemini em 2026
            client = genai.Client(api_key=api_key)
            
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            prompt = st.chat_input("Dúvida de Cálculo ou Química?")
            if prompt:
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    # Contexto focado na UENF e nas suas matérias críticas
                    instrucoes = "Você é um tutor para Jonathan Nunes Martins Faria Dias, aluno de Eng. Civil na UENF. Ajude com Cálculo, Álgebra Linear e Química Geral."
                    response = client.models.generate_content(
                        model='gemini-2.0-flash', 
                        contents=f"{instrucoes}\n\nPergunta: {prompt}"
                    )
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro no Gemini: {e}")

# Replicar a lógica de 'width="stretch"' nas abas de Treino e Notas também.
