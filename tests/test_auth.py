from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

import database
import main
import schemas
from main import criar_usuario, gerar_hash_senha, verificar_senha


def test_gerar_e_verificar_senha_valida():
    # Arrange
    senha_plana = "minhaSenha123"

    # Act
    hash_gerado = gerar_hash_senha(senha_plana)

    # Assert
    assert hash_gerado != senha_plana
    assert verificar_senha(senha_plana, hash_gerado) is True


def test_verificar_senha_incorreta_retorna_false():
    # Arrange
    hash_gerado = gerar_hash_senha("senhaCorreta")

    # Act
    resultado = verificar_senha("senhaErrada", hash_gerado)

    # Assert
    assert resultado is False


def test_criar_usuario_com_campos_vazios_levanta_400(monkeypatch):
    # Arrange
    monkeypatch.setattr(database.engine, "connect", MagicMock())
    monkeypatch.setattr(main.models.Base.metadata, "create_all", MagicMock())

    db_fake = MagicMock()
    payload = schemas.UsuarioCreate(
        nome="   ",
        login="jorgef",
        senha="123",
        role=schemas.RoleUsuario.vendedor,
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        criar_usuario(payload, db=db_fake)

    assert exc_info.value.status_code == 400
    db_fake.add.assert_not_called()
    db_fake.commit.assert_not_called()


def test_criar_usuario_valido_hasheia_senha_e_salva():
    # Arrange
    db_fake = MagicMock()
    payload = schemas.UsuarioCreate(
        nome="Jorge Filho",
        login="jorgef",
        senha="senhaSegura123",
        role=schemas.RoleUsuario.admin,
    )

    def _simular_refresh(obj):
        obj.id = 1

    db_fake.refresh.side_effect = _simular_refresh

    # Act
    resultado = criar_usuario(payload, db=db_fake)

    # Assert
    db_fake.add.assert_called_once()
    db_fake.commit.assert_called_once()
    usuario_criado = db_fake.add.call_args[0][0]
    assert usuario_criado.nome == "Jorge Filho"
    assert usuario_criado.login == "jorgef"
    assert usuario_criado.senha_hash != "senhaSegura123"
    assert verificar_senha("senhaSegura123", usuario_criado.senha_hash) is True
    assert resultado.id == 1