from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db

# Isso cria as tabelas automaticamente no banco de dados na primeira execução
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Estoque Agropecuário", version="1.0")

@app.post("/categorias/", response_model=schemas.CategoriaResponse)
def criar_categoria(categoria: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = models.Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@app.get("/categorias/", response_model=list[schemas.CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categoria).all()

@app.post("/produtos/", response_model=schemas.ProdutoResponse)
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = models.Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.post("/lotes/", response_model=schemas.LoteResponse)
def registrar_lote(lote: schemas.LoteCreate, db: Session = Depends(get_db)):
    # A quantidade disponível inicial é igual à quantidade recebida
    db_lote = models.Lote(**lote.model_dump(), quantidade_disponivel=lote.quantidade_inicial)
    db.add(db_lote)
    db.commit()
    db.refresh(db_lote)
    return db_lote

@app.post("/movimentacoes/saida")
def registrar_saida(lote_id: int, usuario_id: int, quantidade: float, db: Session = Depends(get_db)):
    lote = db.query(models.Lote).filter(models.Lote.id == lote_id).first()
    
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado.")
    if lote.quantidade_disponivel < quantidade:
        raise HTTPException(status_code=400, detail="Estoque insuficiente neste lote.")
    
    nova_movimentacao = models.Movimentacao(
        lote_id=lote_id, 
        usuario_id=usuario_id, 
        quantidade=quantidade, 
        tipo=models.TipoMovimentacao.saida
    )
    
    # Atualiza o saldo do lote
    lote.quantidade_disponivel -= quantidade
    
    db.add(nova_movimentacao)
    db.commit()
    return {"mensagem": "Saída registrada com sucesso!", "saldo_restante": lote.quantidade_disponivel}