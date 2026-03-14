import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime

# --- 1. CONFIGURAÇÃO E TEMA SaaS ---
st.set_page_config(page_title="SupSmart Ultra", layout="wide", page_icon="🛒")

# CSS para Mobile-First e Glassmorphism
st.markdown("""
<style>
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Botões Grandes para Mobile */
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3rem;
        font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
    }
    
    /* Dashboard Moderno */
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.1);
        border-radius: 16px; padding: 20px;
    }
    
    /* Container Flutuante para Total (Mobile) */
    .total-fixed {
        position: fixed; top: 0; left: 0; right: 0; background: #0e1117;
        z-index: 999; padding: 10px; border-bottom: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DADOS (SQLite + PANDAS) ---
def init_db():
    conn = sqlite3.connect('supsmart_pro.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, total REAL, itens_qtd INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS itens_detalhes 
                 (compra_id INTEGER, nome TEXT, preco REAL, qtd REAL, cat TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 3. INTELIGÊNCIA DE ANÁLISE ---
def get_insights():
    df_itens = pd.read_sql("SELECT * FROM itens_detalhes", conn)
    if df_itens.empty: return None, None
    
    # Preço Médio por Item
    precos_medios = df_itens.groupby('nome')['preco'].mean().to_dict()
    
    # Itens Frequentes
    frequentes = df_itens['nome'].value_counts().head(5).index.tolist()
    
    return precos_medios, frequentes

precos_medios, frequentes = get_insights()

# --- 4. GESTÃO DE ESTADO ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- 5. DASHBOARD DE TOPO ---
st.title("SupSmart / Ultra")

df_compras = pd.read_sql("SELECT * FROM compras", conn)
total_carrinho = sum(i['Total'] for i in st.session_state.carrinho)

d1, d2, d3 = st.columns(3)
with d1:
    st.metric("Total Atual", f"R$ {total_carrinho:.2f}")
with d2:
    st.metric("Itens", len(st.session_state.carrinho))
with d3:
    media_mensal = df_compras['total'].mean() if not df_compras.empty else 0
    st.metric("Média Mensal", f"R$ {media_mensal:.2f}")

# --- 6. SEÇÃO: ADICIONAR RÁPIDO (MOBILE-FIRST) ---
with st.expander("⚡ Adicionar Item Rápido", expanded=True):
    with st.form("quick_add", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        nome_q = c1.text_input("Produto", placeholder="Arroz")
        qtd_q = c2.number_input("Qtd", min_value=0.1, value=1.0)
        preco_q = c3.number_input("R$", min_value=0.0, step=0.01)
        
        # Alerta de Preço Médio (Inteligência)
        if precos_medios and nome_q in precos_medios:
            media = precos_medios[nome_q]
            if preco_q > media:
                diff = ((preco_q / media) - 1) * 100
                st.warning(f"⚠️ {diff:.0f}% mais caro que a sua média (R$ {media:.2f})")
        
        if st.form_submit_button("+ ADICIONAR"):
            if nome_q and preco_q > 0:
                st.session_state.carrinho.append({
                    "Cat": "📦 Outros", "Item": nome_q, "Qtd": qtd_q, 
                    "Preço": preco_q, "Total": qtd_q * preco_q
                })
                st.rerun()

# --- 7. ITENS FREQUENTES (SUGESTÃO INTELIGENTE) ---
if frequentes:
    st.write("### ⭐ Comprados com frequência")
    cols_f = st.columns(len(frequentes))
    for i, item in enumerate(frequentes):
        if cols_f[i].button(item, key=f"freq_{item}"):
            st.session_state.carrinho.append({
                "Cat": "📦 Outros", "Item": item, "Qtd": 1.0, 
                "Preço": precos_medios.get(item, 0.0), "Total": precos_medios.get(item, 0.0)
            })
            st.rerun()

# --- 8. ABAS DE NAVEGAÇÃO ---
tab_lista, tab_analise, tab_hist = st.tabs(["🛒 Lista Atual", "📈 Análise", "📜 Histórico"])

with tab_lista:
    if st.session_state.carrinho:
        # Editor de Dados Moderno
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state.carrinho),
            column_config={
                "Cat": st.column_config.SelectboxColumn("Categoria", options=["🍎 Alimentos", "🧴 Higiene", "🧽 Limpeza", "🥤 Bebidas", "📦 Outros"]),
                "Total": st.column_config.NumberColumn(format="R$ %.2f")
            },
            hide_index=True, use_container_width=True
        )
        
        c_fin, c_sha = st.columns(2)
        if c_fin.button("💾 FINALIZAR E SALVAR", type="primary"):
            cur = conn.cursor()
            dt = datetime.now().strftime("%d/%m/%Y %H:%M")
            cur.execute("INSERT INTO compras (data, total, itens_qtd) VALUES (?, ?, ?)", (dt, total_carrinho, len(st.session_state.carrinho)))
            c_id = cur.lastrowid
            for i in st.session_state.carrinho:
                cur.execute("INSERT INTO itens_detalhes VALUES (?, ?, ?, ?, ?)", (c_id, i['Item'], i['Preço'], i['Qtd'], i['Cat']))
            conn.commit()
            st.session_state.carrinho = []
            st.balloons()
            st.rerun()
        
        if c_sha.button("📤 COMPARTILHAR"):
            msg = f"🛒 *Lista SupSmart*\nTotal: R$ {total_carrinho:.2f}\n"
            for i in st.session_state.carrinho:
                msg += f"- {i['Item']}: R$ {i['Total']:.2f}\n"
            st.code(msg) # Simula cópia para área de transferência

with tab_analise:
    if not df_compras.empty:
        df_itens_all = pd.read_sql("SELECT * FROM itens_detalhes", conn)
        
        c_an1, c_an2 = st.columns(2)
        
        with c_an1:
            st.write("### Gastos por Categoria")
            fig_cat = px.pie(df_itens_all, values='preco', names='cat', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_cat, use_container_width=True)
            
        with c_an2:
            st.write("### Insight do Especialista")
            cat_top = df_itens_all.groupby('cat')['preco'].sum().idxmax()
            percent_top = (df_itens_all.groupby('cat')['preco'].sum().max() / df_itens_all['preco'].sum()) * 100
            st.info(f"💡 **Foco de Gasto:** A categoria **{cat_top}** representa **{percent_top:.1f}%** das suas despesas.")

with tab_hist:
    st.dataframe(df_compras.sort_values(by='id', ascending=False), use_container_width=True, hide_index=True)