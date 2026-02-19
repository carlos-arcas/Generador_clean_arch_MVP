from pathlib import Path
import re

import pytest

PATRON_ACCESO_PRIVADOS_AJENOS = re.compile(r"\.\_[a-zA-Z0-9]+\.\_[a-zA-Z0-9]+")
DIRECTORIOS_OBJETIVO = ("presentacion", "aplicacion")
DIRECTORIOS_EXCLUIDOS = {"tests", ".venv", "__pycache__"}

# Lista blanca excepcional: usar solo con justificación arquitectónica explícita.
# Formato: (ruta_relativa_en_posix, numero_linea, fragmento)
LISTA_BLANCA_EXCEPCIONES: set[tuple[str, int, str]] = set()


def _iterar_archivos_python() -> list[Path]:
    raiz = Path(__file__).resolve().parents[2]
    archivos: list[Path] = []

    for directorio in DIRECTORIOS_OBJETIVO:
        base = raiz / directorio
        if not base.exists():
            continue

        for archivo in base.rglob("*.py"):
            if any(parte in DIRECTORIOS_EXCLUIDOS for parte in archivo.parts):
                continue
            archivos.append(archivo)

    return archivos


def test_no_debe_haber_acceso_encadenado_a_privados_ajenos() -> None:
    incidencias: list[str] = []
    raiz = Path(__file__).resolve().parents[2]

    for archivo in _iterar_archivos_python():
        contenido = archivo.read_text(encoding="utf-8")
        for numero_linea, linea in enumerate(contenido.splitlines(), start=1):
            for coincidencia in PATRON_ACCESO_PRIVADOS_AJENOS.finditer(linea):
                fragmento = coincidencia.group(0)
                ruta_relativa = archivo.relative_to(raiz).as_posix()
                clave_excepcion = (ruta_relativa, numero_linea, fragmento)

                if clave_excepcion in LISTA_BLANCA_EXCEPCIONES:
                    continue

                incidencias.append(
                    f"- {ruta_relativa}:{numero_linea} -> {fragmento}"
                )

    # Simulación temporal para validar fallo (mantener comentado):
    # ejemplo = "objeto._interno._detalle"
    # assert not PATRON_ACCESO_PRIVADOS_AJENOS.search(ejemplo)

    if incidencias:
        detalle = "\n".join(incidencias)
        pytest.fail(
            "Se detectó acceso encadenado a atributos privados ajenos:\n"
            f"{detalle}"
        )
