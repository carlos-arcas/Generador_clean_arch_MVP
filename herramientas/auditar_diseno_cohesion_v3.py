from __future__ import annotations

import ast
import argparse
import json
import logging
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

DIRECTORIOS_EXCLUIDOS = {".git", ".venv", "__pycache__", ".pytest_cache", "tests", "herramientas"}

JUSTIFICACIONES: dict[tuple[str, str, int], str] = {}
PATRON_PRIVADOS_ENCADENADOS = re.compile(r"\._[a-zA-Z0-9]+\._[a-zA-Z0-9]+")


@dataclass(frozen=True)
class Hallazgo:
    severidad: str
    categoria: str
    regla: str
    archivo: str
    linea: int
    detalle: str
    justificado: bool = False


@dataclass(frozen=True)
class MetodoAnalizado:
    nombre: str
    linea: int
    lineas: int
    ramas: int


class _ContadorRamas(ast.NodeVisitor):
    def __init__(self) -> None:
        self.ramas = 0

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


def _iterar_archivos_python(raiz: Path) -> list[Path]:
    archivos: list[Path] = []
    for archivo in raiz.rglob("*.py"):
        rel = archivo.relative_to(raiz)
        if any(parte in DIRECTORIOS_EXCLUIDOS for parte in rel.parts):
            continue
        archivos.append(archivo)
    return archivos


def _aplicar_justificacion(hallazgo: Hallazgo) -> Hallazgo:
    clave = (hallazgo.regla, hallazgo.archivo, hallazgo.linea)
    if clave in JUSTIFICACIONES:
        motivo = JUSTIFICACIONES[clave]
        return Hallazgo(
            severidad=hallazgo.severidad,
            categoria=hallazgo.categoria,
            regla=hallazgo.regla,
            archivo=hallazgo.archivo,
            linea=hallazgo.linea,
            detalle=f"{hallazgo.detalle} | justificación: {motivo}",
            justificado=True,
        )
    return hallazgo


def _loc(texto: str) -> int:
    return len(texto.splitlines())


def _es_entrypoint(relativo: str) -> bool:
    if relativo.endswith("/__main__.py"):
        return True
    return relativo.startswith("infraestructura/bootstrap/")


def _analizar_imports(raiz: Path, archivo: Path, arbol: ast.Module) -> list[Hallazgo]:
    hallazgos: list[Hallazgo] = []
    relativo = archivo.relative_to(raiz).as_posix()
    capa = Path(relativo).parts[0] if Path(relativo).parts else ""

    for nodo in ast.walk(arbol):
        modulo = ""
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                modulo = alias.name
                if capa == "presentacion" and modulo.startswith("dominio"):
                    hallazgos.append(
                        Hallazgo("ALTO", "Acoplamiento", "Import prohibido presentacion->dominio", relativo, nodo.lineno, modulo)
                    )
                if capa == "aplicacion" and modulo.startswith("infraestructura"):
                    hallazgos.append(
                        Hallazgo("ALTO", "Acoplamiento", "Import prohibido aplicacion->infraestructura", relativo, nodo.lineno, modulo)
                    )
        if isinstance(nodo, ast.ImportFrom):
            modulo = nodo.module or ""
            if capa == "presentacion" and modulo.startswith("dominio"):
                hallazgos.append(
                    Hallazgo("ALTO", "Acoplamiento", "Import prohibido presentacion->dominio", relativo, nodo.lineno, modulo)
                )
            if capa == "aplicacion" and modulo.startswith("infraestructura"):
                hallazgos.append(
                    Hallazgo("ALTO", "Acoplamiento", "Import prohibido aplicacion->infraestructura", relativo, nodo.lineno, modulo)
                )

    return hallazgos


def _analizar_privados(raiz: Path, archivo: Path, texto: str) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []
    for numero, linea in enumerate(texto.splitlines(), start=1):
        match = PATRON_PRIVADOS_ENCADENADOS.search(linea)
        if match:
            hallazgos.append(
                Hallazgo("ALTO", "Acoplamiento", "Acceso encadenado a privados", relativo, numero, match.group(0))
            )
    return hallazgos


def _analizar_metodos(raiz: Path, archivo: Path, arbol: ast.Module) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []

    funciones: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funciones.append(nodo)

    for funcion in funciones:
        if not hasattr(funcion, "end_lineno"):
            continue
        lineas = int(funcion.end_lineno) - int(funcion.lineno) + 1
        contador = _ContadorRamas()
        contador.visit(funcion)
        ramas = contador.ramas
        if lineas > 60:
            hallazgos.append(
                Hallazgo("MEDIO", "Complejidad", "Método > 60 líneas", relativo, funcion.lineno, f"{funcion.name}: lineas={lineas}")
            )
        if ramas > 5:
            severidad = "ALTO" if ramas > 8 else "MEDIO"
            hallazgos.append(
                Hallazgo(severidad, "Complejidad", "Método con demasiadas ramas", relativo, funcion.lineno, f"{funcion.name}: ramas={ramas}")
            )

    return hallazgos


def _analizar_excepts(raiz: Path, archivo: Path, arbol: ast.Module) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []
    if _es_entrypoint(relativo):
        return hallazgos

    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Try):
            continue
        for handler in nodo.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                severidad = "ALTO" if relativo.startswith("aplicacion/casos_uso/") else "MEDIO"
                hallazgos.append(
                    Hallazgo(severidad, "Manejo de errores", "except Exception fuera de entrypoint", relativo, handler.lineno, "except Exception")
                )

    return hallazgos


def _analizar_cohesion(raiz: Path, archivo: Path, arbol: ast.Module) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    clases_publicas = [n for n in arbol.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
    hallazgos: list[Hallazgo] = []
    if len(clases_publicas) > 6:
        hallazgos.append(
            Hallazgo("MEDIO", "Cohesión", "Archivo con más de 6 clases públicas", relativo, 1, f"clases_publicas={len(clases_publicas)}")
        )
    elif len(clases_publicas) >= 5:
        hallazgos.append(
            Hallazgo("BAJO", "Cohesión", "Concentración sospechosa de clases públicas", relativo, 1, f"clases_publicas={len(clases_publicas)}")
        )
    return hallazgos


def auditar_diseno_cohesion_v3(raiz: Path) -> dict[str, Any]:
    hallazgos: list[Hallazgo] = []

    for archivo in _iterar_archivos_python(raiz):
        relativo = archivo.relative_to(raiz).as_posix()
        texto = archivo.read_text(encoding="utf-8")
        loc = _loc(texto)
        partes = Path(relativo).parts

        if partes and partes[0] in {"presentacion", "aplicacion"}:
            if loc > 500:
                hallazgos.append(Hallazgo("ALTO", "Monolito", "Archivo > 500 LOC", relativo, 1, f"LOC={loc}"))
            elif loc > 400:
                hallazgos.append(Hallazgo("MEDIO", "Monolito", "Archivo > 400 LOC", relativo, 1, f"LOC={loc}"))

        try:
            arbol = ast.parse(texto)
        except SyntaxError as exc:
            LOGGER.warning("No se pudo parsear %s: %s", relativo, exc)
            continue

        hallazgos.extend(_analizar_imports(raiz, archivo, arbol))
        hallazgos.extend(_analizar_privados(raiz, archivo, texto))
        hallazgos.extend(_analizar_metodos(raiz, archivo, arbol))
        hallazgos.extend(_analizar_excepts(raiz, archivo, arbol))
        hallazgos.extend(_analizar_cohesion(raiz, archivo, arbol))

    hallazgos_justificados = [_aplicar_justificacion(h) for h in hallazgos]

    hallazgos_ordenados = sorted(
        hallazgos_justificados,
        key=lambda h: ({"ALTO": 0, "MEDIO": 1, "BAJO": 2}.get(h.severidad, 9), h.archivo, h.linea),
    )

    altos_no_justificados = [h for h in hallazgos_ordenados if h.severidad == "ALTO" and not h.justificado]
    medios = [h for h in hallazgos_ordenados if h.severidad == "MEDIO"]
    bajos = [h for h in hallazgos_ordenados if h.severidad == "BAJO"]

    riesgo = max(0.0, min(10.0, round(10.0 - len(altos_no_justificados) * 1.5 - len(medios) * 0.2 - len(bajos) * 0.05, 2)))

    return {
        "hallazgos": [asdict(h) for h in hallazgos_ordenados],
        "resumen": {
            "ALTO": len([h for h in hallazgos_ordenados if h.severidad == "ALTO"]),
            "MEDIO": len(medios),
            "BAJO": len(bajos),
            "altos_no_justificados": len(altos_no_justificados),
            "riesgo_global": riesgo,
        },
    }


def _parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audita diseño/cohesión v3 del repositorio")
    parser.add_argument(
        "--raiz",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Ruta raíz del repositorio a auditar",
    )
    parser.add_argument("--salida", type=Path, required=True, help="Ruta de salida JSON")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Activa logging DEBUG para mayor detalle",
    )
    return parser.parse_args()


def main() -> int:
    args = _parsear_argumentos()
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    resultado = auditar_diseno_cohesion_v3(args.raiz.resolve())
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("Auditoría v3 escrita en %s", args.salida)
    LOGGER.debug("Resumen v3: %s", resultado.get("resumen", {}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
