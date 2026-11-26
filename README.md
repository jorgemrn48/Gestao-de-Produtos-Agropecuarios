# Sistema de Gestão de Produtos Agropecuários

Sistema full-stack desenvolvido para o gerenciamento operacional, controle de estoque por lotes e acerto de contas financeiro de distribuidoras de produtos agropecuários (como ovos, laticínios e hortifrúti). A aplicação substitui anotações manuais por uma plataforma centralizada com API RESTful, interface web interativa, persistência relacional, testes unitários automatizados e integração contínua.

## Contexto do Negócio e Problemas Resolvidos

Na distribuição de produtos agropecuários, as mercadorias chegam dos produtores/granjas em remessas brutas com volumes, datas e custos variáveis. Após o recebimento, cada carga passa por uma triagem/classificação em produtos específicos (com diferentes unidades de medida e custos atribuídos) antes de ser retirada pelos vendedores para atendimento aos seus clientes.

O sistema resolve três gargalos centrais dessa operação:

1. **Rastreabilidade de Estoque e Lotes:** Substitui controles informais (cadernos e mensagens) pelo registro estruturado de cargas brutas, lotes classificados com data de validade e saldo disponível atualizado automaticamente a cada retirada.
2. **Classificação e Rateio de Custos:** Permite desmembrar uma carga bruta em múltiplos itens classificados com custos unitários atribuídos, respeitando o volume total recebido e impedindo classificações duplicadas da mesma carga.
3. **Acerto de Contas Financeiro:** Consolida o histórico de retiradas por vendedor e os pagamentos realizados, calculando o saldo devedor em aberto para fechamento financeiro transparente entre administradores e vendedores.


## Arquitetura e Tecnologias

O projeto adota uma arquitetura em camadas com separação clara de responsabilidades:

* **Backend (API REST):** Python 3.12, FastAPI, Pydantic v2 e bcrypt para hashing de senhas (main.py, schemas.py).
* **Persistência e ORM:** SQLAlchemy e PyMySQL conectados a um banco **MySQL 8.0** conteinerizado (database.py, models.py, docker-compose.yml).
* **Frontend (Interface Web):** Aplicação interativa em **Streamlit** (app.py) com controle de acesso por perfil (admin e vendedor).
* **Qualidade e CI:** Testes unitários isolados com **Pytest** (tests/) executados automaticamente via **GitHub Actions** (.github/workflows/ci.yml).


## Funcionalidades e Regras de Negócio

### Perfis de Acesso
* **Administrador (admin):** Visualiza o dashboard geral de estoque e cargas, cadastra produtos e usuários, registra entradas de cargas brutas, realiza a classificação de lotes, registra retiradas e efetua o lançamento de pagamentos no acerto de contas.
* **Vendedor:** Consulta lotes disponíveis em estoque, registra suas próprias retiradas e acompanha seu histórico de retiradas, pagamentos e saldo em aberto.

### Principais Regras de Negócio
* **Unidades de Medida e Quantidades:** Todas as retiradas exigem quantidade positiva. Produtos contabilizados em unidades discretas (Bandeja, Unidade, Caixa, Dúzia) aceitam apenas valores inteiros, enquanto unidades contínuas (como Kg) aceitam valores decimais.
* **Controle de Saldo e Classificação:** Não é permitido retirar quantidade superior ao saldo disponível no lote, nem classificar uma carga já classificada ou com soma de itens superior ao volume bruto recebido.
* **Segurança:** Senhas são armazenadas exclusivamente como hash (bcrypt) e endpoints/telas administrativas são restritos ao perfil `admin`.


## Como Executar o Projeto

### Pré-requisitos
* Python 3.12+
* Docker e Docker Compose

### 1. Subir o banco de dados MySQL
Na raiz do projeto, inicie o container do MySQL:
docker compose up -d

### 2. Criar e ativar o ambiente virtual Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 3. Iniciar a API
Em um terminal com a venv ativada:
uvicorn main:app --reload

A documentação ficará disponível em http://localhost:8000/docs


### 4. Ativar a interface Web
Em um segundo terminal com a venv ativada:
streamlit run app.py

A aplicação abrirá automaticamente em http://localhost:8501

### Testes Automatizados e Integração Contínua
O sistema possui 14 testes untários organizados por domínio em tests/:
tests/test_auth.py: geração e validação de hash de senhas, rejeição de senha incorreta e valiação na criação de usuário
tests/test_retiradas.py: validação de quantidades, restrição de valores inteiros vs decimais, bloqueio por saldo insuficiente e baixa automática de estoque
tests/test_admin.py: cadastro de produtos, registro de carga bruta, validação de volume/existência na classificação e registro de pagamentos.

Para executar os testes localmente sem depender do servidor MySQL ativo:
SKIP_DB_INIT=1 python -m pytest -v

A cada push ou pull_request nas branches desenvolvimento e main, o workflow .github/workflows/ci.yml executa automaticamente todos os testes no GitHub Actions.
