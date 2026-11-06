from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Gestão (Custeio, Classificação e Financeiro)", version="4.0")

@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = models.Usuario(
        nome=usuario.nome,
        login=usuario.login,
        senha_hash=usuario.senha, 
        role=usuario.role
    )
    db.add(db_usuario)
    try:
        db.commit()
        db.refresh(db_usuario)
        return db_usuario
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="O Login já existe.")

@app.get("/usuarios/", response_model=list[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

@app.post("/login/")
def login(req: schemas.LoginData, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.login == req.login, 
        models.Usuario.senha_hash == req.senha
    ).first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais incorretas")
    return {"id": usuario.id, "nome": usuario.nome, "role": usuario.role.value}

@app.post("/produtos/", response_model=schemas.ProdutoResponse)
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = models.Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.get("/produtos/", response_model=list[schemas.ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(models.Produto).all()

@app.post("/cargas/", response_model=schemas.CargaBrutaResponse)
def registrar_carga(carga: schemas.CargaBrutaCreate, db: Session = Depends(get_db)):
    db_carga = models.CargaBruta(**carga.model_dump())
    db.add(db_carga)
    db.commit()
    db.refresh(db_carga)
    return db_carga

@app.get("/cargas/", response_model=list[schemas.CargaBrutaResponse])
def listar_cargas(db: Session = Depends(get_db)):
    return db.query(models.CargaBruta).all()

@app.post("/estoque/", response_model=list[schemas.EstoqueClassificadoResponse])
def classificar_estoque(estoques: list[schemas.EstoqueClassificadoCreate], db: Session = Depends(get_db)):
    if not estoques:
        raise HTTPException(status_code=400, detail="Lista vazia.")
    
    carga_id = estoques[0].carga_id
    carga = db.query(models.CargaBruta).filter(models.CargaBruta.id == carga_id).first()
    
    if not carga:
        raise HTTPException(status_code=404, detail="Carga não encontrada.")
        
    classificacao_existente = db.query(models.EstoqueClassificado).filter(models.EstoqueClassificado.carga_id == carga_id).first()
    if classificacao_existente:
        raise HTTPException(status_code=400, detail="Classificação já realizada para esta carga.")
        
    qtd_total_classificada = sum(est.quantidade_inicial for est in estoques)
    if qtd_total_classificada > carga.quantidade_total:
        raise HTTPException(status_code=400, detail="Quantidades excedem o volume recebido.")
    
    itens_criados = []
    for est in estoques:
        est_dict = est.model_dump()
        est_dict['data_validade'] = est_dict.get('data_validade') or carga.data_validade
        db_estoque = models.EstoqueClassificado(**est_dict, quantidade_disponivel=est.quantidade_inicial)
        db.add(db_estoque)
        itens_criados.append(db_estoque)
    
    db.commit()
    for item in itens_criados: db.refresh(item)
    return itens_criados

@app.get("/estoque/", response_model=list[schemas.EstoqueClassificadoResponse])
def listar_estoque(db: Session = Depends(get_db)):
    return db.query(models.EstoqueClassificado).all()

@app.post("/retiradas/", response_model=schemas.RetiradaResponse)
def registrar_retirada(retirada: schemas.RetiradaCreate, db: Session = Depends(get_db)):
    estoque = db.query(models.EstoqueClassificado).filter(models.EstoqueClassificado.id == retirada.estoque_id).first()
    if not estoque or estoque.quantidade_disponivel < retirada.quantidade:
        raise HTTPException(status_code=400, detail="Saldo insuficiente.")
    
    nova_retirada = models.Retirada(**retirada.model_dump())
    estoque.quantidade_disponivel -= retirada.quantidade
    
    db.add(nova_retirada)
    db.commit()
    db.refresh(nova_retirada)
    return nova_retirada

@app.get("/retiradas/", response_model=list[schemas.RetiradaResponse])
def listar_retiradas(db: Session = Depends(get_db)):
    return db.query(models.Retirada).all()

@app.post("/pagamentos/", response_model=schemas.PagamentoResponse)
def registrar_pagamento(pagamento: schemas.PagamentoCreate, db: Session = Depends(get_db)):
    novo_pagamento = models.Pagamento(**pagamento.model_dump())
    db.add(novo_pagamento)
    db.commit()
    db.refresh(novo_pagamento)
    return novo_pagamento

@app.get("/pagamentos/", response_model=list[schemas.PagamentoResponse])
def listar_pagamentos(db: Session = Depends(get_db)):
    return db.query(models.Pagamento).all()