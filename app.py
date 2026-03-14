import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone

# --- 1. AJUSTE DE FUSO HORÁRIO (BRASÍLIA) ---
def get_agora_br():
    fuso_br = timezone(timedelta(hours=-3))
    return datetime.now(fuso_br)

# --- 2. BANCO DE DADOS (COM COLUNA LIMITE) ---
def get_db_connection():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER, limite REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT, medida TEXT)''')
    
    # Auto-fix: garante que a coluna limite existe
    cursor.execute("PRAGMA table_info(compras)")
    colunas = [row[1] for row in cursor.fetchall()]
    if 'limite' not in colunas:
        cursor.execute("ALTER TABLE compras ADD COLUMN limite REAL DEFAULT 500.0")
    conn.commit()
    return conn

conn = get_db_connection()

# --- 3. INTERFACE SaaS ---
st.set_page_config(page_title="SupSmart Pro", layout="wide")

# Sidebar para configurações de orçamento
with st.sidebar:
    st.header("⚙️ Ajustes")
    orcamento_meta = st.number_input("Definir Meta de Gasto (R$):", min_value=0.0, value=500.0, step=50.0)

st.title("SupSmart / Dashboard")

# --- 4. LÓGICA DE DADOS ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

total_atual = sum(item['Total'] for item in st.session_state.carrinho)
df_hist = pd.read_sql("SELECT * FROM compras", conn)

# --- 5. GRÁFICO DE ORÇAMENTO (TELA INICIAL) ---
col_met, col_gra = st.columns([1, 2])

with col_met:
    st.metric("No Carrinho", f"R$ {total_atual:.2f}")
    st.metric("Meta Definida", f"R$ {orcamento_meta:.2f}")
    
    restante = orcamento_meta - total_atual
    if restante >= 0:
        st.success(f"Disponível: R$ {restante:.2f}")
    else:
        st.error(f"Estourou: R$ {abs(restante):.2f}")

with col_gra:
    # Gráfico tipo Gauge (Velocímetro) de Orçamento
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_atual,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Progresso do Orçamento"},
        gauge = {
            'axis': {'range': [None, max(orcamento_meta, total_atual + 100)]},
            'bar': {'color': "#1E90FF"},
            'steps': [
                {'range': [0, orcamento_meta * 0.8], 'color': "rgba(0, 255, 0, 0.1)"},
                {'range': [orcamento_meta * 0.8, orcamento_meta], 'color': "rgba(255, 165, 0, 0.2)"},
                {'range': [orcamento_meta, max(orcamento_meta, total_atual + 100)], 'color': "rgba(255, 0, 0, 0.2)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': orcamento_meta
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)

# --- 6. FORMULÁRIO E FINALIZAÇÃO ---
st.divider()
# ... (Aqui viria o seu código de adicionar itens e a tabela do carrinho) ...

if st.button("✅ FINALIZAR COMPRA", type="primary", use_container_width=True):
    if st.session_state.carrinho:
        cur = conn.cursor()
        data_br = get_agora_br().strftime("%d/%m/%Y %H:%M")
        cur.execute("INSERT INTO compras (data, total, itens_qtd, limite) VALUES (?, ?, ?, ?)", 
                    (data_br, total_atual, len(st.session_state.carrinho), orcamento_meta))
        # (Lógica para salvar itens_detalhes permanece igual)
        conn.commit()
        st.session_state.carrinho = []
        st.balloons()
        st.rerun()