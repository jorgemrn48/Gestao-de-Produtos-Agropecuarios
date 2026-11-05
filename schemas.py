from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class RoleUsuario(str, Enum):
    admin = "admin"
    vendedor = "vendedor"

class TipoMovimentacao(str, Enum):
    entrada = "entrada"
    saida = "saida"
    descarte = "descarte"

# --- CATEGORIAS ---
class CategoriaBase(BaseModel):
    nome: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int
    class Config:
        from_attributes = True

# --- PRODUTOS ---
class ProdutoBase(BaseModel):
    nome: str
    unidade_medida: str
    categoria_id: int

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int
    class Config:
        from_attributes = True

# --- LOTES ---
class LoteBase(BaseModel):
    produto_id: int
    quantidade_inicial: float
    preco_nota: float
    data_validade: Optional[datetime] = None

class LoteCreate(LoteBase):
    pass

class LoteResponse(LoteBase):
    id: int
    quantidade_disponivel: float
    data_recebimento: datetime
    class Config:
        from_attributes = True

# --- USUÁRIOS ---
class UsuarioBase(BaseModel):
    nome: str
    login: str
    role: RoleUsuario = RoleUsuario.vendedor

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int
    class Config:
        from_attributes = True