import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta, timezone

# --- 1. FUSO HORÁRIO BRASÍLIA ---
def get_agora_br():
    fuso_br = timezone(timedelta(hours=-3))
    return datetime.now(fuso_br)

# --- 2. BANCO DE DADOS (ESTÁVEL) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER, limite REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    # Reparo de colunas silencioso
    cursor.execute("PRAGMA table_info(compras)")
    colunas = [row[1] for row in cursor.fetchall()]
    if 'limite' not in colunas:
        cursor.execute("ALTER TABLE compras ADD COLUMN limite REAL DEFAULT 500.0")
    conn.commit()
    return conn

conn = get_db_connection()

# --- 3. ESTILIZAÇÃO (CARD DESIGN) ---
st.set_page_config(page_title="SupSmart Pro", layout="wide")

st.markdown("""
<style>
    .card-orcamento {
        background-color: #1e2129;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    .metric-label { color: #8b949e; font-size: 14px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #ffffff; }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGICA DE ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

total_carrinho = sum(item['Total'] for item in st.session_state.carrinho)

# --- 5. O NOVO CARD DE ORÇAMENTO ---
with st.container():
    st.markdown('<div class="card-orcamento">', unsafe_allow_html=True)
    
    col_input, col_info = st.columns([1, 2])
    
    with col_input:
        orcamento_meta = st.number_input("Definir Meta (R$)", min_value=0.0, value=500.0, step=50.0)
    
    with col_info:
        porcentagem = min(total_carrinho / orcamento_meta, 1.0) if orcamento_meta > 0 else 0
        cor_barra = "green" if porcentagem < 0.8 else "orange" if porcentagem < 1.0 else "red"
        
        st.markdown(f"<span class='metric-label'>Gasto Atual:</span> <span class='metric-value'>R$ {total_carrinho:.2f}</span>", unsafe_allow_html=True)
        st.progress(porcentagem)
        
        restante = orcamento_meta - total_carrinho
        if restante >= 0:
            st.caption(f"✅ Você ainda tem R$ {restante:.2f} disponíveis")
        else:
            st.caption(f"⚠️ Atenção: Orçamento estourado em R$ {abs(restante):.2f}")
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. LISTA DE COMPRAS (COMPACTA) ---
st.subheader("🛒 Itens no Carrinho")

# ... (Seu código de st.data_editor e botões de adicionar aqui) ...

if st.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
    if st.session_state.carrinho:
        cur = conn.cursor()
        data_br = get_agora_br().strftime("%d/%m/%Y %H:%M")
        cur.execute("INSERT INTO compras (data, total, itens_qtd, limite) VALUES (?, ?, ?, ?)", 
                    (data_br, total_carrinho, len(st.session_state.carrinho), orcamento_meta))
        conn.commit()
        st.session_state.carrinho = []
        st.success("Compra salva com sucesso!")
        st.rerun()