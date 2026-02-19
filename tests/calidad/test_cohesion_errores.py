from __future__ import annotations

from pathlib import Path


def test_paquete_errores_existe() -> None:
    raiz = Path(__file__).resolve().parents[2]
    paquete_errores = raiz / "aplicacion" / "errores"

    assert paquete_errores.is_dir()
    assert (paquete_errores / "__init__.py").is_file()
    assert not (raiz / "aplicacion" / "errores.py").exists()


def test_no_hay_megamodulo_de_errores() -> None:
    raiz = Path(__file__).resolve().parents[2]
    paquete_errores = raiz / "aplicacion" / "errores"
    maximo_clases_por_archivo = 6

    for archivo in paquete_errores.glob("*.py"):
        contenido = archivo.read_text(encoding="utf-8")
        clases = [linea for linea in contenido.splitlines() if linea.strip().startswith("class ")]
        assert len(clases) <= maximo_clases_por_archivo, (
            f"El archivo {archivo.relative_to(raiz)} excede el umbral de clases: {len(clases)}"
        )
