from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class RoleUsuario(str, Enum):
    admin = "admin"
    vendedor = "vendedor"

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

class ProdutoBase(BaseModel):
    nome: str
    unidade_medida: str

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int
    class Config:
        from_attributes = True

class CargaBrutaBase(BaseModel):
    descricao: str
    custo_total: float
    quantidade_total: float
    data_validade: Optional[datetime] = None
    data_recebimento: datetime

class CargaBrutaCreate(CargaBrutaBase):
    pass

class CargaBrutaResponse(CargaBrutaBase):
    id: int
    class Config:
        from_attributes = True

class EstoqueClassificadoBase(BaseModel):
    carga_id: int
    produto_id: int
    quantidade_inicial: float
    preco_custo_atribuido: float
    data_validade: Optional[datetime] = None

class EstoqueClassificadoCreate(EstoqueClassificadoBase):
    pass

class EstoqueClassificadoResponse(EstoqueClassificadoBase):
    id: int
    carga_id: int
    produto_id: int
    quantidade_disponivel: float
    preco_custo_atribuido: float
    data_validade: Optional[datetime] = None
    class Config:
        from_attributes = True

class RetiradaBase(BaseModel):
    estoque_id: int
    vendedor_id: int
    quantidade: float

class RetiradaCreate(RetiradaBase):
    pass

class RetiradaResponse(RetiradaBase):
    id: int
    estoque_id: int
    vendedor_id: int
    quantidade: float
    data_retirada: datetime
    class Config:
        from_attributes = True

class PagamentoBase(BaseModel):
    vendedor_id: int
    valor: float

class PagamentoCreate(PagamentoBase):
    pass

class PagamentoResponse(PagamentoBase):
    id: int
    data_pagamento: datetime
    class Config:
        from_attributes = True

class LoginData(BaseModel):
    login: str
    senha: str