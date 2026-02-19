from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

UMBRAL_LOC_CANDIDATO = 350
UMBRAL_LOC_BLOQUEANTE_PRESENTACION = 450
UMBRAL_METODO_LINEAS = 55
UMBRAL_METODO_RAMAS = 12
UMBRAL_METODO_RETURNS = 6
UMBRAL_METODO_SCORE = 24
UMBRAL_METODOS_PUBLICOS_CLASE = 10
UMBRAL_CLASES_ARCHIVO = 4

DIRECTORIOS_EXCLUIDOS = {".git", ".venv", "__pycache__", ".pytest_cache", "tests"}
PATRON_ACCESO_PRIVADO_ENCADENADO = re.compile(r"\._[a-zA-Z0-9]+\._[a-zA-Z0-9]+")


@dataclass(frozen=True)
class Hallazgo:
    severidad: str
    categoria: str
    regla: str
    archivo: str
    linea: int
    detalle: str


class _AnalizadorMetodo(ast.NodeVisitor):
    def __init__(self) -> None:
        self.ramas = 0
        self.returns = 0

    def visit_If(self, node: ast.If) -> Any:
        self.ramas += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> Any:
        self.ramas += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> Any:
        self.ramas += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> Any:
        self.ramas += 1
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> Any:
        self.returns += 1
        self.generic_visit(node)


def _iterar_archivos_python(raiz: Path) -> list[Path]:
    archivos: list[Path] = []
    for archivo in raiz.rglob("*.py"):
        relativa = archivo.relative_to(raiz)
        if any(parte in DIRECTORIOS_EXCLUIDOS for parte in relativa.parts):
            continue
        if relativa.parts and relativa.parts[0] == "herramientas":
            continue
        archivos.append(archivo)
    return archivos


def _loc_archivo(texto: str) -> int:
    return len(texto.splitlines())


def _extraer_imports_sospechosos(raiz: Path, archivo: Path, texto: str) -> list[Hallazgo]:
    hallazgos: list[Hallazgo] = []
    relativo = archivo.relative_to(raiz).as_posix()
    partes = Path(relativo).parts
    if not partes:
        return hallazgos

    capa = partes[0]
    for numero_linea, linea in enumerate(texto.splitlines(), start=1):
        importacion = linea.strip()
        if not importacion.startswith(("import ", "from ")):
            continue

        if capa == "presentacion" and (
            importacion.startswith("import dominio") or importacion.startswith("from dominio")
        ):
            hallazgos.append(
                Hallazgo(
                    severidad="ALTO",
                    categoria="Acoplamiento",
                    regla="Import prohibido presentacion->dominio",
                    archivo=relativo,
                    linea=numero_linea,
                    detalle=importacion,
                )
            )

        if capa == "aplicacion" and (
            importacion.startswith("import infraestructura")
            or importacion.startswith("from infraestructura")
        ):
            hallazgos.append(
                Hallazgo(
                    severidad="ALTO",
                    categoria="Acoplamiento",
                    regla="Import prohibido aplicacion->infraestructura",
                    archivo=relativo,
                    linea=numero_linea,
                    detalle=importacion,
                )
            )

    return hallazgos


def _extraer_accesos_privados(raiz: Path, archivo: Path, texto: str) -> list[Hallazgo]:
    hallazgos: list[Hallazgo] = []
    relativo = archivo.relative_to(raiz).as_posix()
    for numero_linea, linea in enumerate(texto.splitlines(), start=1):
        coincidencia = PATRON_ACCESO_PRIVADO_ENCADENADO.search(linea)
        if not coincidencia:
            continue
        hallazgos.append(
            Hallazgo(
                severidad="ALTO",
                categoria="Acoplamiento",
                regla="Acceso encadenado a privados",
                archivo=relativo,
                linea=numero_linea,
                detalle=coincidencia.group(0),
            )
        )
    return hallazgos


def _score_complejidad(lineas: int, ramas: int, returns: int) -> int:
    return lineas // 6 + ramas * 2 + returns


def _analizar_clases_y_metodos(raiz: Path, archivo: Path, texto: str) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []

    try:
        modulo = ast.parse(texto)
    except SyntaxError as exc:
        LOGGER.warning("No se pudo parsear %s: %s", relativo, exc)
        return hallazgos

    clases = [n for n in modulo.body if isinstance(n, ast.ClassDef)]
    if len(clases) >= UMBRAL_CLASES_ARCHIVO:
        hallazgos.append(
            Hallazgo(
                severidad="MEDIO",
                categoria="Cohesión",
                regla="Muchas clases en el mismo archivo",
                archivo=relativo,
                linea=1,
                detalle=f"clases={len(clases)}",
            )
        )

    for clase in clases:
        metodos_publicos = [
            n for n in clase.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
        ]
        if len(metodos_publicos) > UMBRAL_METODOS_PUBLICOS_CLASE:
            hallazgos.append(
                Hallazgo(
                    severidad="MEDIO",
                    categoria="SRP",
                    regla="Clase con demasiados métodos públicos",
                    archivo=relativo,
                    linea=clase.lineno,
                    detalle=f"{clase.name}: metodos_publicos={len(metodos_publicos)}",
                )
            )

        for metodo in [n for n in clase.body if isinstance(n, ast.FunctionDef)]:
            if not hasattr(metodo, "end_lineno"):
                continue
            lineas = int(metodo.end_lineno) - int(metodo.lineno) + 1
            analizador = _AnalizadorMetodo()
            analizador.visit(metodo)
            score = _score_complejidad(lineas, analizador.ramas, analizador.returns)
            if (
                lineas >= UMBRAL_METODO_LINEAS
                or analizador.ramas >= UMBRAL_METODO_RAMAS
                or analizador.returns >= UMBRAL_METODO_RETURNS
                or score >= UMBRAL_METODO_SCORE
            ):
                severidad = "ALTO" if score >= UMBRAL_METODO_SCORE + 6 else "MEDIO"
                hallazgos.append(
                    Hallazgo(
                        severidad=severidad,
                        categoria="Complejidad",
                        regla="Método todo-en-uno",
                        archivo=relativo,
                        linea=metodo.lineno,
                        detalle=(
                            f"{clase.name}.{metodo.name}: lineas={lineas}, "
                            f"ramas={analizador.ramas}, returns={analizador.returns}, score={score}"
                        ),
                    )
                )

    return hallazgos


def auditar_diseno_cohesion(raiz: Path) -> dict[str, Any]:
    hallazgos: list[Hallazgo] = []
    archivos_loc_altos: list[tuple[str, int]] = []

    for archivo in _iterar_archivos_python(raiz):
        texto = archivo.read_text(encoding="utf-8")
        relativo = archivo.relative_to(raiz).as_posix()
        loc = _loc_archivo(texto)
        partes = Path(relativo).parts

        if partes and partes[0] in {"presentacion", "aplicacion"} and loc > UMBRAL_LOC_CANDIDATO:
            hallazgos.append(
                Hallazgo(
                    severidad="MEDIO",
                    categoria="Cohesión",
                    regla="Archivo monolítico por LOC",
                    archivo=relativo,
                    linea=1,
                    detalle=f"LOC={loc}",
                )
            )

        if partes and partes[0] == "presentacion" and loc > UMBRAL_LOC_BLOQUEANTE_PRESENTACION:
            archivos_loc_altos.append((relativo, loc))

        hallazgos.extend(_extraer_imports_sospechosos(raiz, archivo, texto))
        hallazgos.extend(_extraer_accesos_privados(raiz, archivo, texto))
        hallazgos.extend(_analizar_clases_y_metodos(raiz, archivo, texto))

    # Señal complementaria: capturas amplias `except Exception`.
    for archivo in _iterar_archivos_python(raiz):
        texto = archivo.read_text(encoding="utf-8")
        relativo = archivo.relative_to(raiz).as_posix()
        try:
            modulo = ast.parse(texto)
        except SyntaxError:
            continue

        for nodo in ast.walk(modulo):
            if not isinstance(nodo, ast.Try):
                continue
            for handler in nodo.handlers:
                tipo = handler.type
                if isinstance(tipo, ast.Name) and tipo.id == "Exception":
                    hallazgos.append(
                        Hallazgo(
                            severidad="MEDIO",
                            categoria="Complejidad",
                            regla="Captura amplia de excepciones",
                            archivo=relativo,
                            linea=handler.lineno,
                            detalle="except Exception as ...",
                        )
                    )

    hallazgos_ordenados = sorted(
        hallazgos,
        key=lambda h: ({"ALTO": 0, "MEDIO": 1, "BAJO": 2}.get(h.severidad, 9), h.archivo, h.linea),
    )

    return {
        "hallazgos": [h.__dict__ for h in hallazgos_ordenados],
        "metricas": {
            "total_hallazgos": len(hallazgos_ordenados),
            "por_severidad": {
                "ALTO": sum(1 for h in hallazgos_ordenados if h.severidad == "ALTO"),
                "MEDIO": sum(1 for h in hallazgos_ordenados if h.severidad == "MEDIO"),
                "BAJO": sum(1 for h in hallazgos_ordenados if h.severidad == "BAJO"),
            },
            "archivos_presentacion_loc_mayor_450": archivos_loc_altos,
        },
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    raiz = Path(__file__).resolve().parents[1]
    resultado = auditar_diseno_cohesion(raiz)
    LOGGER.info("Auditoría finalizada: %s hallazgos", resultado["metricas"]["total_hallazgos"])
