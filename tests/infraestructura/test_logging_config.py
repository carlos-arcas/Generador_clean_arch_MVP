import logging
from pathlib import Path
import sys

from infraestructura.logging_config import configurar_logging


def test_configurar_logging_crea_archivos_y_filtra_secretos(tmp_path: Path) -> None:
    configurar_logging(str(tmp_path))
    logger = logging.getLogger("prueba_logging")

    logger.info("mensaje visible")
    logger.error("este mensaje contiene token y no debe persistirse")

    seguimiento = tmp_path / "seguimiento.log"
    crashes = tmp_path / "crashes.log"

    assert seguimiento.exists()
    assert crashes.exists()
    assert "mensaje visible" in seguimiento.read_text(encoding="utf-8")
    assert "token" not in seguimiento.read_text(encoding="utf-8").lower()


def test_configurar_logging_instala_excepthook() -> None:
    anterior = sys.excepthook
    configurar_logging("logs")
    assert sys.excepthook is not anterior
