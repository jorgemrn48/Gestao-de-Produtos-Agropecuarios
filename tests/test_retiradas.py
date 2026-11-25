from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

import main
import schemas
from main import registrar_retirada, validar_quantidade_retirada


def test_retirada_quantidade_zero_ou_negativa_levanta_400():
    # Arrange / Act & Assert
    with pytest.raises(HTTPException) as exc_zero:
        validar_quantidade_retirada(0, "Bandeja")
    assert exc_zero.value.status_code == 400

    with pytest.raises(HTTPException) as exc_neg:
        validar_quantidade_retirada(-5, "Bandeja")
    assert exc_neg.value.status_code == 400


def test_retirada_decimal_em_bandeja_levanta_400_e_em_kg_passa():
    # Arrange / Act & Assert
    with pytest.raises(HTTPException) as exc_bandeja:
        validar_quantidade_retirada(1.5, "Bandeja")
    assert exc_bandeja.value.status_code == 400

    # Unidade contínua (Kg) permite decimal
    validar_quantidade_retirada(2.5, "Kg")


def test_registrar_retirada_acima_do_saldo_levanta_400():
    # Arrange
    lote_fake = SimpleNamespace(
        id=10,
        quantidade_disponivel=5.0,
        produto=SimpleNamespace(unidade_medida="Bandeja"),
    )

    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = lote_fake

    db_fake = MagicMock()
    db_fake.query.return_value = query_mock

    retirada_invalida = schemas.RetiradaCreate(
        estoque_id=10,
        vendedor_id=2,
        quantidade=8.0,
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        registrar_retirada(retirada_invalida, db=db_fake)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Saldo insuficiente."
    assert lote_fake.quantidade_disponivel == 5.0
    db_fake.commit.assert_not_called()


def test_registrar_retirada_valida_desconta_saldo_sem_banco_real(monkeypatch):
    # Arrange
    lote_fake = SimpleNamespace(
        id=10,
        quantidade_disponivel=20.0,
        produto=SimpleNamespace(unidade_medida="Bandeja"),
    )

    query_mock = MagicMock()
    query_mock.filter.return_value.first.return_value = lote_fake

    db_fake = MagicMock()
    db_fake.query.return_value = query_mock

    def _simular_refresh(obj):
        obj.id = 99
        obj.data_retirada = "2026-11-25T17:00:00"

    db_fake.refresh.side_effect = _simular_refresh
    monkeypatch.setattr(main.models, "Retirada", lambda **kwargs: SimpleNamespace(**kwargs))

    retirada_valida = schemas.RetiradaCreate(
        estoque_id=10,
        vendedor_id=2,
        quantidade=4.0,
    )

    # Act
    criada = registrar_retirada(retirada_valida, db=db_fake)

    # Assert
    assert lote_fake.quantidade_disponivel == 16.0
    assert criada.quantidade == 4.0
    assert criada.vendedor_id == 2
    db_fake.add.assert_called_once()
    db_fake.commit.assert_called_once()