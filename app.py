import streamlit as st
import requests
import pandas as pd

# URL da nossa API FastAPI
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Gestão Agropecuária", layout="wide")
st.sidebar.title("Módulos")
menu = st.sidebar.radio("Navegação", ["Dashboard", "Categorias e Produtos", "Entrada (Lotes)", "Saída (Movimentação)"])

if menu == "Dashboard":
    st.title("📦 Dashboard de Estoque")
    st.markdown("Visão geral do sistema. Nos próximos dias, integraremos o dataset público do IBGE aqui e criaremos as consultas SQL avançadas.")
    
    # Teste de conexão simples para validar o ambiente
    try:
        res = requests.get(f"{API_URL}/categorias/")
        if res.status_code == 200:
            st.success("✅ Conexão com a API (FastAPI) e Banco de Dados (MySQL) estabelecida com sucesso!")
            categorias = res.json()
            if categorias:
                st.write("Categorias já cadastradas no banco:")
                st.dataframe(pd.DataFrame(categorias))
    except requests.exceptions.ConnectionError:
        st.error("❌ API offline. Lembre-se de rodar o uvicorn no terminal.")

elif menu == "Categorias e Produtos":
    st.title("Cadastros Básicos")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Nova Categoria")
        nome_categoria = st.text_input("Nome da Categoria (ex: Sementes, Defensivos)")
        if st.button("Cadastrar Categoria"):
            res = requests.post(f"{API_URL}/categorias/", json={"nome": nome_categoria})
            if res.status_code == 200:
                st.success("Categoria cadastrada com sucesso!")
            else:
                st.error("Erro ao cadastrar categoria.")
                
    with col2:
        st.subheader("Novo Produto")
        nome_produto = st.text_input("Nome do Produto")
        unidade = st.selectbox("Unidade de Medida", ["Kg", "Litro", "Saca", "Unidade"])
        
        # Busca categorias dinamicamente no banco para preencher o select
        categorias = []
        try:
            cat_req = requests.get(f"{API_URL}/categorias/")
            if cat_req.status_code == 200:
                categorias = cat_req.json()
        except:
            pass
            
        if categorias:
            cat_dict = {c["nome"]: c["id"] for c in categorias}
            cat_selecionada = st.selectbox("Vincular à Categoria", list(cat_dict.keys()))
            
            if st.button("Cadastrar Produto"):
                payload = {
                    "nome": nome_produto,
                    "unidade_medida": unidade,
                    "categoria_id": cat_dict[cat_selecionada]
                }
                res = requests.post(f"{API_URL}/produtos/", json=payload)
                if res.status_code == 200:
                    st.success(f"{nome_produto} cadastrado com sucesso!")
                else:
                    st.error("Erro ao cadastrar produto.")
        else:
            st.warning("⚠️ Cadastre pelo menos uma categoria ao lado primeiro.")

elif menu == "Entrada (Lotes)":
    st.title("📥 Registro de Entrada")
    st.info("Interface preparada. Amanhã conectaremos os inputs à rota POST /lotes/.")

elif menu == "Saída (Movimentação)":
    st.title("📤 Registro de Saída")
    st.info("Interface preparada. Amanhã conectaremos os inputs à rota POST /movimentacoes/saida/.")