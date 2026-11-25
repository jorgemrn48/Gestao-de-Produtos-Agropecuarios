from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

import main
import schemas
from main import classificar_estoque, criar_produto, registrar_carga, registrar_pagamento


def test_criar_produto_valido_salva_e_retorna_id(monkeypatch):
    # Arrange
    db_fake = MagicMock()
    payload = schemas.ProdutoCreate(nome="Ovos Brancos", unidade_medida="Bandeja")

    def _simular_refresh(obj):
        obj.id = 1

    db_fake.refresh.side_effect = _simular_refresh
    monkeypatch.setattr(main.models, "Produto", lambda **kwargs: SimpleNamespace(**kwargs))

    # Act
    criado = criar_produto(payload, db=db_fake)

    # Assert
    assert criado.id == 1
    assert criado.nome == "Ovos Brancos"
    assert criado.unidade_medida == "Bandeja"
    db_fake.add.assert_called_once()
    db_fake.commit.assert_called_once()


def test_registrar_carga_com_custo_zero_bonificacao_permitida(monkeypatch):
    # Arrange
    db_fake = MagicMock()
    agora = datetime(2026, 11, 25, 12, 0, 0)
    payload = schemas.CargaBrutaCreate(
        descricao="Bonificação Granja Central",
        custo_total=0.0,
        quantidade_total=50.0,
        data_validade=agora,
        data_recebimento=agora,
    )

    def _simular_refresh(obj):
        obj.id = 7

    db_fake.refresh.side_effect = _simular_refresh
    monkeypatch.setattr(main.models, "CargaBruta", lambda **kwargs: SimpleNamespace(**kwargs))

    # Act
    carga = registrar_carga(payload, db=db_fake)

    # Assert
    assert carga.id == 7
    assert carga.custo_total == 0.0
    assert carga.quantidade_total == 50.0
    db_fake.commit.assert_called_once()


def test_classificar_estoque_excedendo_quantidade_da_carga_levanta_400():
    # Arrange
    carga_fake = SimpleNamespace(
        id=1,
        quantidade_total=100.0,
        data_validade=None,
    )

    # 1ª chamada: busca CargaBruta -> retorna carga_fake
    # 2ª chamada: busca EstoqueClassificado existente -> retorna None (ainda não classificada)
    query_carga = MagicMock()
    query_carga.filter.return_value.first.return_value = carga_fake

    query_estoque_existente = MagicMock()
    query_estoque_existente.filter.return_value.first.return_value = None

    db_fake = MagicMock()
    db_fake.query.side_effect = [query_carga, query_estoque_existente]

    itens = [
        schemas.EstoqueClassificadoCreate(
            carga_id=1,
            produto_id=2,
            quantidade_inicial=120.0,
            preco_custo_atribuido=12.5,
        )
    ]

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        classificar_estoque(itens, db=db_fake)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Quantidades excedem o volume recebido."
    db_fake.commit.assert_not_called()


def test_classificar_estoque_carga_inexistente_levanta_404():
    # Arrange
    query_carga = MagicMock()
    query_carga.filter.return_value.first.return_value = None

    db_fake = MagicMock()
    db_fake.query.return_value = query_carga

    itens = [
        schemas.EstoqueClassificadoCreate(
            carga_id=999,
            produto_id=2,
            quantidade_inicial=10.0,
            preco_custo_atribuido=10.0,
        )
    ]

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        classificar_estoque(itens, db=db_fake)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Carga não encontrada."
    db_fake.commit.assert_not_called()


def test_classificar_estoque_valido_define_quantidade_disponivel_igual_inicial(monkeypatch):
    # Arrange
    validade_base = datetime(2026, 12, 15, 0, 0, 0)
    carga_fake = SimpleNamespace(
        id=3,
        quantidade_total=100.0,
        data_validade=validade_base,
    )

    class FakeEstoqueClassificado:
        carga_id = "carga_id"

        def __init__(self, **kwargs):
            for chave, valor in kwargs.items():
                setattr(self, chave, valor)

    query_carga = MagicMock()
    query_carga.filter.return_value.first.return_value = carga_fake

    query_estoque_existente = MagicMock()
    query_estoque_existente.filter.return_value.first.return_value = None

    db_fake = MagicMock()
    db_fake.query.side_effect = [query_carga, query_estoque_existente]
    db_fake.refresh.side_effect = lambda item: setattr(item, "id", 55)

    monkeypatch.setattr(main.models, "EstoqueClassificado", FakeEstoqueClassificado)

    itens = [
        schemas.EstoqueClassificadoCreate(
            carga_id=3,
            produto_id=1,
            quantidade_inicial=40.0,
            preco_custo_atribuido=15.0,
        )
    ]

    # Act
    criados = classificar_estoque(itens, db=db_fake)

    # Assert
    assert len(criados) == 1
    assert criados[0].id == 55
    assert criados[0].quantidade_inicial == 40.0
    assert criados[0].quantidade_disponivel == 40.0
    assert criados[0].data_validade == validade_base
    db_fake.commit.assert_called_once()


def test_registrar_pagamento_valido_salva_e_retorna_id(monkeypatch):
    # Arrange
    db_fake = MagicMock()
    payload = schemas.PagamentoCreate(vendedor_id=2, valor=150.0)

    def _simular_refresh(obj):
        obj.id = 12
        obj.data_pagamento = datetime(2026, 11, 25, 18, 0, 0)

    db_fake.refresh.side_effect = _simular_refresh
    monkeypatch.setattr(main.models, "Pagamento", lambda **kwargs: SimpleNamespace(**kwargs))

    # Act
    pagamento = registrar_pagamento(payload, db=db_fake)

    # Assert
    assert pagamento.id == 12
    assert pagamento.vendedor_id == 2
    assert pagamento.valor == 150.0
    db_fake.add.assert_called_once()
    db_fake.commit.assert_called_once()