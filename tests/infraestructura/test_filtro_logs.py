import logging

from infraestructura.logging_config import FiltroSecretos


def test_filtro_logs_oculta_password() -> None:
    filtro = FiltroSecretos()
    record = logging.makeLogRecord(
        {
            "msg": "Error de conexión password=mi_clave token=abcd1234",
            "args": (),
            "levelno": logging.ERROR,
            "levelname": "ERROR",
        }
    )

    filtro.filter(record)

    mensaje = record.getMessage().lower()
    assert "mi_clave" not in mensaje
    assert "abcd1234" not in mensaje
    assert "password=***" in mensaje
    assert "token=***" in mensaje
