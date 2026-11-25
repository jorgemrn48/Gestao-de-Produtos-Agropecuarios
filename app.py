import streamlit as st
import requests
import pandas as pd
from datetime import date

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Gestão de Estoque Agro", layout="wide")

if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Acesso ao Sistema")
    aba_login, aba_cadastro = st.tabs(["Fazer Login", "Criar Primeiro Utilizador"])
    with aba_login:
        with st.form("form_login"):
            login_user = st.text_input("Login")
            login_senha = st.text_input("Palavra-passe", type="password")
            if st.form_submit_button("Entrar"):
                res = requests.post(f"{API_URL}/login/", json={"login": login_user, "senha": login_senha})
                if res.status_code == 200:
                    dados = res.json()
                    st.session_state.update({"logged_in": True, "user_id": dados['id'], "user_nome": dados['nome'], "user_role": dados['role']})
                    st.rerun()
                else: 
                    st.error("Credenciais inválidas.")
    with aba_cadastro:
        with st.form("form_cadastro"):
            nome_cad = st.text_input("Nome Completo")
            login_cad = st.text_input("Login")
            senha_cad = st.text_input("Palavra-passe", type="password")
            role_cad = st.selectbox("Perfil", ["admin", "vendedor"])
            if st.form_submit_button("Cadastrar"):
                res = requests.post(f"{API_URL}/usuarios/", json={"nome": nome_cad, "login": login_cad, "senha": senha_cad, "role": role_cad})
                if res.status_code == 200:
                    st.success("Criado com sucesso! Pode fazer o login ao lado.")
                else:
                    st.error("Erro ao criar utilizador. O nome de login já deve estar em uso.")
    st.stop()

st.sidebar.title(f"Olá, {st.session_state.user_nome}!")
if st.sidebar.button("Sair da Conta"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
if st.session_state.user_role == "admin":
    opcoes = ["Dashboard", "Produtos (Catálogo)", "1. Receber Carga Bruta", "2. Classificar Estoque", "3. Registrar Retirada", "4. Histórico e Rastreabilidade", "5. Acerto de Contas"]
else:
    opcoes = ["Produtos (Catálogo)", "3. Registrar Retirada", "Minhas Retiradas e Dívida"]

menu = st.sidebar.radio("Navegação", opcoes)

if menu == "Dashboard":
    st.title("📦 Dashboard Geral")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Estoque Classificado Atual")
        try:
            estoque = requests.get(f"{API_URL}/estoque/").json()
            produtos = {p['id']: p['nome'] for p in requests.get(f"{API_URL}/produtos/").json()}
            if estoque:
                dados_limpos = [{
                    "Produto": produtos.get(e['produto_id'], "Desconhecido"),
                    "Custo": f"R$ {e['preco_custo_atribuido']:.2f}",
                    "Validade": e['data_validade'][:10] if e['data_validade'] else "-",
                    "Saldo Disponível": e['quantidade_disponivel']
                } for e in estoque if e['quantidade_disponivel'] > 0]
                
                if dados_limpos:
                    df_agrupado = pd.DataFrame(dados_limpos).groupby(['Produto', 'Custo', 'Validade'], as_index=False)['Saldo Disponível'].sum()
                    st.dataframe(df_agrupado)
                else:
                    st.info("Todos os lotes classificados estão zerados.")
        except: pass
    with col2:
        st.subheader("Últimas Cargas Recebidas")
        try:
            res_cargas = requests.get(f"{API_URL}/cargas/")
            if res_cargas.status_code == 200 and res_cargas.json():
                df_cargas = pd.DataFrame(res_cargas.json())
                df_cargas['data_recebimento'] = df_cargas['data_recebimento'].str[:10]
                df_cargas.rename(columns={'id': 'ID', 'descricao': 'Descrição', 'quantidade_total': 'Qtd Total', 'custo_total': 'Custo (R$)', 'data_recebimento': 'Data de Recebimento'}, inplace=True)
                st.dataframe(df_cargas[['ID', 'Descrição', 'Qtd Total', 'Custo (R$)', 'Data de Recebimento']])
        except: pass

elif menu == "Produtos (Catálogo)":
    st.title("🏷️ Catálogo de Produtos Finais")
    if st.session_state.user_role == "admin":
        with st.form("form_prod", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            unidade = st.selectbox("Unidade de Medida", ["Bandeja", "Unidade", "Kg", "Litro"])
            if st.form_submit_button("Salvar Produto"):
                if requests.post(f"{API_URL}/produtos/", json={"nome": nome, "unidade_medida": unidade}).status_code == 200:
                    st.toast("✅ Produto cadastrado!")
                    st.rerun()
    try:
        lista_prod = requests.get(f"{API_URL}/produtos/").json()
        if lista_prod: st.dataframe(pd.DataFrame(lista_prod)[['id', 'nome', 'unidade_medida']])
        else: st.info("Nenhum produto cadastrado.")
    except: pass

elif menu == "1. Receber Carga Bruta":
    st.title("🚛 Entrada de Carga Bruta")
    with st.form("form_carga", clear_on_submit=True):
        descricao = st.text_input("Descrição (Ex: Carga Granja X - 07/11)")
        col1, col2 = st.columns(2)
        with col1:
            custo = st.number_input("Custo Total (R$)", min_value=0.0, format="%.2f")
            recebimento = st.date_input("Data de Recebimento", max_value=date.today())
        with col2:
            qtd_total = st.number_input("Quantidade Total (Bruta)", min_value=0.01)
            validade = st.date_input("Data de Validade Base", min_value=date.today())
        
        if st.form_submit_button("Registar Carga"):
            payload = {"descricao": descricao, "custo_total": custo, "quantidade_total": qtd_total, "data_validade": validade.isoformat() + "T00:00:00", "data_recebimento": recebimento.isoformat() + "T00:00:00"}
            if requests.post(f"{API_URL}/cargas/", json=payload).status_code == 200:
                st.toast("✅ Carga registada com sucesso!")
                st.rerun()

elif menu == "2. Classificar Estoque":
    st.title("🗂️ Fila de Classificação")
    cargas_req = requests.get(f"{API_URL}/cargas/").json() if requests.get(f"{API_URL}/cargas/").status_code == 200 else []
    estoque_req = requests.get(f"{API_URL}/estoque/").json() if requests.get(f"{API_URL}/estoque/").status_code == 200 else []
    produtos = requests.get(f"{API_URL}/produtos/").json() if requests.get(f"{API_URL}/produtos/").status_code == 200 else []
    
    if not cargas_req:
        st.info("⚠️ Não há cargas registradas no sistema ainda.")
    else:
        cargas_classificadas = {e['carga_id'] for e in estoque_req}
        cargas_pendentes = [c for c in cargas_req if c['id'] not in cargas_classificadas]
        
        if not cargas_pendentes:
            st.success("🎉 Todas as cargas já foram classificadas! Nenhuma pendência na fila.")
        elif not produtos:
            st.warning("⚠️ Cadastre Produtos no catálogo primeiro para poder classificar.")
        else:
            map_cargas = {f"Carga #{c['id']} - {c['descricao']} (Qtd: {c['quantidade_total']})": c['id'] for c in cargas_pendentes}
            map_produtos = {p['nome']: p['id'] for p in produtos}
            carga_sel = st.selectbox("Selecione a Carga Pendente", list(map_cargas.keys()))
            
            df_template = pd.DataFrame({"Produto": [list(map_produtos.keys())[0]], "Quantidade": [0.0], "Custo (R$)": [0.0]})
            edited_df = st.data_editor(df_template, num_rows="dynamic", use_container_width=True, column_config={
                "Produto": st.column_config.SelectboxColumn("Produto", options=list(map_produtos.keys()), required=True)
            })
            
            if st.button("Gerar Lotes"):
                records = edited_df.to_dict('records')
                payload = [{"carga_id": map_cargas[carga_sel], "produto_id": map_produtos[r["Produto"]], "quantidade_inicial": r["Quantidade"], "preco_custo_atribuido": r["Custo (R$)"]} for r in records if r["Quantidade"] > 0]
                if payload:
                    res = requests.post(f"{API_URL}/estoque/", json=payload)
                    if res.status_code == 200:
                        st.toast("✅ Estoque classificado com sucesso!")
                        st.rerun()
                    else: st.error(res.json().get('detail', 'Erro'))
                else:
                    st.warning("Preencha quantidades maiores que zero.")

elif menu == "3. Registrar Retirada":
    st.title("📤 Movimentação de Saída")
    estoque = requests.get(f"{API_URL}/estoque/").json() if requests.get(f"{API_URL}/estoque/").status_code == 200 else []
    produtos = {p['id']: p['nome'] for p in requests.get(f"{API_URL}/produtos/").json()} if requests.get(f"{API_URL}/produtos/").status_code == 200 else {}
    cargas = {c['id']: c['descricao'] for c in requests.get(f"{API_URL}/cargas/").json()} if requests.get(f"{API_URL}/cargas/").status_code == 200 else {}
    
    opcoes_estoque = {}
    detalhes_lote = {}
    for e in estoque:
        if e['quantidade_disponivel'] > 0:
            nome = produtos.get(e['produto_id'], "Desc.")
            origem = cargas.get(e['carga_id'], "Desc.")
            val = e['data_validade'][:10] if e['data_validade'] else "-"
            label = f"{nome} | R$ {e['preco_custo_atribuido']:.2f} | Vence {val} | Origem: Carga #{e['carga_id']} ({origem})"
            opcoes_estoque[label] = e['id']
            detalhes_lote[label] = float(e['quantidade_disponivel'])
            
    if opcoes_estoque:
        estoque_sel = st.selectbox("Selecione o Lote (Preço | Validade | Origem)", list(opcoes_estoque.keys()))
        saldo_atual = detalhes_lote[estoque_sel]
        
        st.info(f"Saldo físico disponível neste lote: **{saldo_atual}**")
        quantidade = st.number_input("Quantidade a Retirar", min_value=0.1, max_value=saldo_atual, step=1.0)
        
        if st.button("Registar Saída"):
            payload = {"estoque_id": opcoes_estoque[estoque_sel], "vendedor_id": st.session_state.user_id, "quantidade": quantidade}
            if requests.post(f"{API_URL}/retiradas/", json=payload).status_code == 200:
                st.toast("✅ Saída registada!")
                st.rerun()
    else: st.warning("Não há estoque disponível.")

elif menu == "4. Histórico e Rastreabilidade":
    st.title("🔎 Histórico e Rastreabilidade")
    cargas_req = requests.get(f"{API_URL}/cargas/")
    if cargas_req.status_code == 200 and cargas_req.json():
        cargas = cargas_req.json()
        map_cargas = {f"Carga #{c['id']} - {c['descricao']}": c['id'] for c in cargas}
        carga_id = map_cargas[st.selectbox("Selecione a Carga Bruta", list(map_cargas.keys()))]
        carga_info = next(c for c in cargas if c['id'] == carga_id)
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        estoque_carga = [e for e in requests.get(f"{API_URL}/estoque/").json() if e['carga_id'] == carga_id]
        
        with col_a:
            st.write("### 📥 Dados de Entrada")
            st.write(f"**Descrição:** {carga_info['descricao']}")
            st.write(f"**Data de Recebimento:** {carga_info.get('data_recebimento', '-')[:10]}")
            st.write(f"**Data de Validade Base:** {carga_info.get('data_validade', '-')[:10] if carga_info.get('data_validade') else '-'}")
            st.write(f"**Qtd Bruta Recebida:** {carga_info['quantidade_total']}")
            
        with col_b:
            st.write("### ⚖️ Balanço")
            if not estoque_carga:
                st.info("⚠️ Aguardando Classificação")
            else:
                qtd_classificada = sum(e['quantidade_inicial'] for e in estoque_carga)
                desperdicio = carga_info['quantidade_total'] - qtd_classificada
                st.write(f"**Qtd Total Classificada:** {qtd_classificada}")
                st.success(f"**Desperdício / Perda Registada:** {desperdicio}")
        
        st.markdown("---")
        if estoque_carga:
            st.write("### 🗂️ Desmembramento (Lotes Gerados)")
            produtos_req = requests.get(f"{API_URL}/produtos/")
            produtos = {p['id']: p['nome'] for p in produtos_req.json()} if produtos_req.status_code == 200 else {}
            
            tabela_lotes = []
            for e in estoque_carga:
                tabela_lotes.append({
                    "Produto": produtos.get(e['produto_id'], "Desconhecido"),
                    "Qtd Inicial": e['quantidade_inicial'],
                    "Saldo Atual": e['quantidade_disponivel'],
                    "Custo Atribuído": f"R$ {e['preco_custo_atribuido']:.2f}"
                })
            st.dataframe(pd.DataFrame(tabela_lotes))
            
            st.write("### 📤 Histórico de Retiradas")
            lotes_ids = [e['id'] for e in estoque_carga]
            ret_req = requests.get(f"{API_URL}/retiradas/")
            
            if ret_req.status_code == 200:
                retiradas = [r for r in ret_req.json() if r['estoque_id'] in lotes_ids]
                if retiradas:
                    usuarios_req = requests.get(f"{API_URL}/usuarios/")
                    usuarios = {u['id']: u['nome'] for u in usuarios_req.json()} if usuarios_req.status_code == 200 else {}
                    
                    tabela_retiradas = []
                    for r in retiradas:
                        lote = next(e for e in estoque_carga if e['id'] == r['estoque_id'])
                        tabela_retiradas.append({
                            "Data": r['data_retirada'][:10],
                            "Produto": produtos.get(lote['produto_id'], "Desconhecido"),
                            "Vendedor": f"{usuarios.get(r['vendedor_id'], 'Desc.')} (ID: {r['vendedor_id']})",
                            "Qtd Retirada": r['quantidade']
                        })
                    st.dataframe(pd.DataFrame(tabela_retiradas))
                else:
                    st.info("Nenhuma retirada registada para os lotes desta carga.")
    else:
        st.info("⚠️ Não há lotes/cargas cadastrados no sistema ainda.")

# NOVA FUNCIONALIDADE: ACERTO DE CONTAS (ADMIN)
elif menu == "5. Acerto de Contas":
    st.title("💰 Financeiro: Acerto com Vendedores")
    usuarios = [u for u in requests.get(f"{API_URL}/usuarios/").json() if u['role'] == 'vendedor']
    
    if usuarios:
        map_vendedores = {f"{u['nome']} (ID {u['id']})": u['id'] for u in usuarios}
        vendedor_sel = st.selectbox("Selecione o Vendedor", list(map_vendedores.keys()))
        vendedor_id = map_vendedores[vendedor_sel]
        
        # Calcula a dívida
        retiradas = [r for r in requests.get(f"{API_URL}/retiradas/").json() if r['vendedor_id'] == vendedor_id]
        lotes_info = {e['id']: e['preco_custo_atribuido'] for e in requests.get(f"{API_URL}/estoque/").json()}
        valor_devido = sum(r['quantidade'] * lotes_info.get(r['estoque_id'], 0) for r in retiradas)
        
        pagamentos = [p for p in requests.get(f"{API_URL}/pagamentos/").json() if p['vendedor_id'] == vendedor_id]
        valor_pago = sum(p['valor'] for p in pagamentos)
        
        saldo_aberto = valor_devido - valor_pago
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Valor Total Retirado", f"R$ {valor_devido:.2f}")
        col2.metric("Valor Já Pago", f"R$ {valor_pago:.2f}")
        col3.metric("Saldo Devedor Atual", f"R$ {saldo_aberto:.2f}", delta=f"R$ {-saldo_aberto:.2f}" if saldo_aberto > 0 else "Quitado", delta_color="inverse")
        
        st.markdown("---")
        col_form, col_hist = st.columns([1, 1])
        
        with col_form:
            st.subheader("Registrar Novo Pagamento")
            with st.form("form_pagamento", clear_on_submit=True):
                valor = st.number_input("Valor Recebido (R$)", min_value=0.1, max_value=float(saldo_aberto) if saldo_aberto > 0 else 10000.0)
                if st.form_submit_button("Confirmar Pagamento"):
                    if requests.post(f"{API_URL}/pagamentos/", json={"vendedor_id": vendedor_id, "valor": valor}).status_code == 200:
                        st.toast("✅ Pagamento registado!")
                        st.rerun()
                        
        with col_hist:
            st.subheader("Histórico de Pagamentos")
            if pagamentos:
                df_pagamentos = pd.DataFrame([{
                    "Data": p['data_pagamento'][:10],
                    "Valor Pago": f"R$ {p['valor']:.2f}"
                } for p in pagamentos])
                # Ordenar para mostrar o mais recente primeiro
                st.dataframe(df_pagamentos.sort_values(by="Data", ascending=False), use_container_width=True)
            else:
                st.info("Nenhum pagamento registrado para este vendedor.")
    else: 
        st.warning("Não há vendedores cadastrados.")

# NOVA FUNCIONALIDADE: EXTRATO DO VENDEDOR
elif menu == "Minhas Retiradas e Dívida":
    st.title("💸 Meu Extrato Financeiro")
    
    retiradas = [r for r in requests.get(f"{API_URL}/retiradas/").json() if r['vendedor_id'] == st.session_state.user_id]
    lotes_info = {e['id']: e['preco_custo_atribuido'] for e in requests.get(f"{API_URL}/estoque/").json()}
    valor_devido = sum(r['quantidade'] * lotes_info.get(r['estoque_id'], 0) for r in retiradas)
    
    pagamentos = [p for p in requests.get(f"{API_URL}/pagamentos/").json() if p['vendedor_id'] == st.session_state.user_id]
    valor_pago = sum(p['valor'] for p in pagamentos)
    
    col1, col2 = st.columns(2)
    col1.metric("Total em Mercadoria (R$)", f"R$ {valor_devido:.2f}")
    col2.metric("Minha Dívida Atual", f"R$ {valor_devido - valor_pago:.2f}")
    
    st.markdown("---")
    col_ret, col_pag = st.columns(2)
    
    with col_ret:
        st.subheader("Histórico de Retiradas")
        if retiradas:
            produtos = {p['id']: p['nome'] for p in requests.get(f"{API_URL}/produtos/").json()}
            lotes_prod = {e['id']: e['produto_id'] for e in requests.get(f"{API_URL}/estoque/").json()}
            
            df_ret = pd.DataFrame([{
                "Data": r['data_retirada'][:10],
                "Produto": produtos.get(lotes_prod.get(r['estoque_id'], 0), "Desc."),
                "Qtd": r['quantidade'],
                "Valor": f"R$ {r['quantidade'] * lotes_info.get(r['estoque_id'], 0):.2f}"
            } for r in retiradas])
            st.dataframe(df_ret.sort_values(by="Data", ascending=False), use_container_width=True)
        else:
            st.info("Nenhuma retirada registada.")
            
    with col_pag:
        st.subheader("Meus Pagamentos")
        if pagamentos:
            df_pag = pd.DataFrame([{
                "Data": p['data_pagamento'][:10],
                "Valor Pago": f"R$ {p['valor']:.2f}"
            } for p in pagamentos])
            st.dataframe(df_pag.sort_values(by="Data", ascending=False), use_container_width=True)
        else:
            st.info("Nenhum pagamento efetuado ainda.")