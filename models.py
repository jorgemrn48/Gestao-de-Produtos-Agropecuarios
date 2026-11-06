from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import datetime
import enum

Base = declarative_base()

class RoleUsuario(enum.Enum):
    admin = "admin"
    vendedor = "vendedor"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    login = Column(String(50), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleUsuario), default=RoleUsuario.vendedor, nullable=False)
    
    retiradas = relationship("Retirada", back_populates="vendedor")
    pagamentos = relationship("Pagamento", back_populates="vendedor")

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    unidade_medida = Column(String(20), nullable=False)
    
    lotes_classificados = relationship("EstoqueClassificado", back_populates="produto")

class CargaBruta(Base):
    __tablename__ = "cargas_brutas"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(200), nullable=False)
    custo_total = Column(Float, nullable=False)
    quantidade_total = Column(Float, nullable=False)
    data_validade = Column(DateTime, nullable=True)
    data_recebimento = Column(DateTime, default=datetime.datetime.utcnow)
    
    estoque_gerado = relationship("EstoqueClassificado", back_populates="carga_origem")

class EstoqueClassificado(Base):
    __tablename__ = "estoque_classificado"
    id = Column(Integer, primary_key=True, index=True)
    carga_id = Column(Integer, ForeignKey("cargas_brutas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    
    quantidade_inicial = Column(Float, nullable=False)
    quantidade_disponivel = Column(Float, nullable=False)
    preco_custo_atribuido = Column(Float, nullable=False)
    data_validade = Column(DateTime, nullable=True)
    
    carga_origem = relationship("CargaBruta", back_populates="estoque_gerado")
    produto = relationship("Produto", back_populates="lotes_classificados")
    retiradas = relationship("Retirada", back_populates="estoque")

class Retirada(Base):
    __tablename__ = "retiradas"
    id = Column(Integer, primary_key=True, index=True)
    estoque_id = Column(Integer, ForeignKey("estoque_classificado.id"), nullable=False)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    quantidade = Column(Float, nullable=False)
    data_retirada = Column(DateTime, default=datetime.datetime.utcnow)
    
    estoque = relationship("EstoqueClassificado", back_populates="retiradas")
    vendedor = relationship("Usuario", back_populates="retiradas")

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    valor = Column(Float, nullable=False)
    data_pagamento = Column(DateTime, default=datetime.datetime.utcnow)
    
    vendedor = relationship("Usuario", back_populates="pagamentos")