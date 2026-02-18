import hashlib
from pathlib import Path

from infraestructura.calculadora_hash_real import CalculadoraHashReal


def test_calculadora_hash_real_calcula_sha256(tmp_path: Path) -> None:
    ruta = tmp_path / "demo.txt"
    ruta.write_text("contenido", encoding="utf-8")

    hash_real = CalculadoraHashReal().calcular_sha256(str(ruta))

    esperado = hashlib.sha256("contenido".encode("utf-8")).hexdigest()
    assert hash_real == esperado
