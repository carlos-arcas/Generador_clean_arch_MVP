from __future__ import annotations

from pathlib import Path
import re


PATRON_IMPORT = re.compile(r"^\s*import\s+([\w\.]+)")
PATRON_FROM = re.compile(r"^\s*from\s+([\w\.]+)\s+import\b")
DIRECTORIOS_IGNORADOS = {"tests", ".venv", "__pycache__"}
ARCHIVO_IGNORADO = Path("infraestructura/bootstrap/__init__.py")
EXCEPCIONES_TEMPORALES = {
    Path("presentacion/wizard_proyecto.py"),
    Path("aplicacion/casos_uso/crear_plan_desde_blueprints.py"),
    Path("aplicacion/casos_uso/auditar_proyecto_generado.py"),
    Path("aplicacion/casos_uso/generacion/generar_proyecto_mvp.py"),
}


class ViolacionArquitectura:
    def __init__(self, archivo: str, linea_numero: int, linea: str, regla: str) -> None:
        self.archivo = archivo
        self.linea_numero = linea_numero
        self.linea = linea
        self.regla = regla

    def formatear(self) -> str:
        return (
            f"{self.archivo}:{self.linea_numero} -> {self.regla}. "
            f"Línea detectada: {self.linea.strip()}"
        )


def _iterar_archivos_python(raiz: Path) -> list[Path]:
    archivos: list[Path] = []
    for archivo in raiz.rglob("*.py"):
        relativa = archivo.relative_to(raiz)
        if any(parte in DIRECTORIOS_IGNORADOS for parte in relativa.parts):
            continue
        if relativa == ARCHIVO_IGNORADO:
            continue
        if relativa in EXCEPCIONES_TEMPORALES:
            continue
        archivos.append(archivo)
    return archivos


def _extraer_modulo_importado(linea: str) -> str | None:
    coincidencia_import = PATRON_IMPORT.match(linea)
    if coincidencia_import:
        return coincidencia_import.group(1)

    coincidencia_from = PATRON_FROM.match(linea)
    if coincidencia_from:
        return coincidencia_from.group(1)

    return None


def _es_import_infraestructura_prohibido(linea: str) -> bool:
    modulo = _extraer_modulo_importado(linea)
    if not modulo:
        return False
    if modulo == "infraestructura.bootstrap" or modulo.startswith("infraestructura.bootstrap."):
        return False
    return modulo == "infraestructura" or modulo.startswith("infraestructura.")


def _es_import_presentacion_prohibido_en_aplicacion(linea: str) -> bool:
    modulo = _extraer_modulo_importado(linea)
    if not modulo:
        return False
    return modulo == "presentacion" or modulo.startswith("presentacion.")


def _analizar_archivo(raiz: Path, archivo: Path) -> list[ViolacionArquitectura]:
    violaciones: list[ViolacionArquitectura] = []
    relativa = archivo.relative_to(raiz)
    contenido = archivo.read_text(encoding="utf-8")

    for indice, linea in enumerate(contenido.splitlines(), start=1):
        if relativa.parts[0] == "aplicacion":
            if _es_import_infraestructura_prohibido(linea) or _es_import_presentacion_prohibido_en_aplicacion(linea):
                violaciones.append(
                    ViolacionArquitectura(
                        archivo=relativa.as_posix(),
                        linea_numero=indice,
                        linea=linea,
                        regla=(
                            "Regla 1 violada "
                            "(aplicacion no puede depender de infraestructura/presentacion)"
                        ),
                    )
                )

        if relativa.parts[0] == "dominio":
            modulo = _extraer_modulo_importado(linea)
            if modulo and (
                modulo == "aplicacion"
                or modulo.startswith("aplicacion.")
                or modulo == "infraestructura"
                or modulo.startswith("infraestructura.")
                or modulo == "presentacion"
                or modulo.startswith("presentacion.")
            ):
                violaciones.append(
                    ViolacionArquitectura(
                        archivo=relativa.as_posix(),
                        linea_numero=indice,
                        linea=linea,
                        regla=(
                            "Regla 2 violada "
                            "(dominio no puede depender de aplicacion/infraestructura/presentacion)"
                        ),
                    )
                )

        if relativa.parts[0] == "presentacion":
            if _es_import_infraestructura_prohibido(linea):
                violaciones.append(
                    ViolacionArquitectura(
                        archivo=relativa.as_posix(),
                        linea_numero=indice,
                        linea=linea,
                        regla=(
                            "Regla 3 violada "
                            "(presentacion no puede depender de infraestructura salvo infraestructura.bootstrap y submódulos)"
                        ),
                    )
                )

    return violaciones


def test_dependencias_entre_capas_clean_architecture() -> None:
    raiz = Path(__file__).resolve().parents[2]
    violaciones: list[ViolacionArquitectura] = []

    for archivo in _iterar_archivos_python(raiz):
        violaciones.extend(_analizar_archivo(raiz=raiz, archivo=archivo))

    if violaciones:
        mensaje = "\n".join(v.formatear() for v in violaciones)
        raise AssertionError(
            "Se detectaron violaciones de arquitectura entre capas:\n"
            f"{mensaje}"
        )
