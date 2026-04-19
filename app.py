import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from google import genai
import datetime

# ─── CONFIGURAÇÃO MOBILE-FIRST ────────────────────────────────
st.set_page_config(page_title="OPERAÇÃO RESGATE", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS PARA MATAR AS BARRIGAS E MELHORAR O VISUAL ─────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    /* Ajuste das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: #1e2130; border-radius: 5px; padding: 5px 10px; color: #888; font-size: 12px;
    }
    .stTabs [aria-selected="true"] { background: #1F3864 !important; color: white !important; }
    /* Estilo do chat */
    .stChatMessage { background-color: #1e2130; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── CONEXÃO ──────────────────────────────────────────────────
conn = st.connection("gsheets", type=GSheetsConnection)

# ─── CABEÇALHO ────────────────────────────────────────────────
hoje = datetime.date.today()
st.subheader(f"⚡ Domingo, {hoje.strftime('%d/%m')}")

# ─── ABAS ─────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📚 Estudo", "💪 Treino", "🎓 Notas", "🤖 IA"])

def load(sheet_name):
    try:
        return conn.read(worksheet=sheet_name).reset_index(drop=True)
    except:
        return None

# --- ABA 2: ESTUDOS (COM AJUSTE DE LARGURA) ---
with tab2:
    st.write("📝 **Registro de Civil - UENF**")
    df_e = load("📚 Registro de Estudos")
    if df_e is not None:
        # 'width="stretch"' remove os avisos do log e as barrigas
        df_edit = st.data_editor(df_e, num_rows="dynamic", width="stretch")
        if st.button("💾 Salvar Estudos", width="stretch"):
            conn.update(worksheet="📚 Registro de Estudos", data=df_edit)
            st.success("✅ Sincronizado!")

# --- ABA 5: IA (COM MODELO 1.5 PARA EVITAR COTA) ---
with tab5:
    st.write("🤖 **Tutor Gemini Online**")
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    if "chat" not in st.session_state:
        st.session_state.chat = []

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Dúvida de Álgebra ou Química?"):
        if not api_key:
            st.error("Erro: Adicione GEMINI_API_KEY no topo dos Secrets!")
        else:
            st.session_state.chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    client = genai.Client(api_key=api_key)
                    ctx = "Jonathan, aluno de Eng. Civil na UENF. Ajude com Álgebra e Química."
                    # Trocado para 1.5-flash por ser mais estável na cota gratuita
                    r = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=f"{ctx}\n\n{prompt}"
                    )
                    st.markdown(r.text)
                    st.session_state.chat.append({"role": "assistant", "content": r.text})
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ Cota atingida! O Google limitou o uso gratuito por agora. Tente de novo em 1 minuto.")
                    else:
                        st.error(f"Erro na IA: {e}")

# (Repita a lógica do load para as outras abas conforme o código anterior)
