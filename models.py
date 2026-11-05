from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
import datetime
import enum

Base = declarative_base()

class RoleUsuario(enum.Enum):
    admin = "admin"
    vendedor = "vendedor"

class TipoMovimentacao(enum.Enum):
    entrada = "entrada"
    saida = "saida"
    descarte = "descarte"

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    login = Column(String(50), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleUsuario), default=RoleUsuario.vendedor, nullable=False)
    
    movimentacoes = relationship("Movimentacao", back_populates="usuario")

class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)
    
    produtos = relationship("Produto", back_populates="categoria")

class Produto(Base):
    __tablename__ = "produtos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    unidade_medida = Column(String(20), nullable=False) # Ex: Kg, Litro, Saca
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    
    categoria = relationship("Categoria", back_populates="produtos")
    lotes = relationship("Lote", back_populates="produto")

class Lote(Base):
    __tablename__ = "lotes"
    
    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade_inicial = Column(Float, nullable=False)
    quantidade_disponivel = Column(Float, nullable=False)
    preco_nota = Column(Float, nullable=False)
    data_recebimento = Column(DateTime, default=datetime.datetime.utcnow)
    data_validade = Column(DateTime, nullable=True)
    
    produto = relationship("Produto", back_populates="lotes")
    movimentacoes = relationship("Movimentacao", back_populates="lote")

class Movimentacao(Base):
    __tablename__ = "movimentacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    quantidade = Column(Float, nullable=False)
    tipo = Column(Enum(TipoMovimentacao), nullable=False)
    data_movimentacao = Column(DateTime, default=datetime.datetime.utcnow)
    
    lote = relationship("Lote", back_populates="movimentacoes")
    usuario = relationship("Usuario", back_populates="movimentacoes")