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
PATRON_PRIVADOS_ENCADENADOS = re.compile(r"\._[a-zA-Z0-9]+\._[a-zA-Z0-9]+")
SEVERIDAD_ORDEN = {"ALTO": 0, "MEDIO": 1, "BAJO": 2}

CAPAS_PRINCIPALES = {"presentacion", "aplicacion", "dominio", "infraestructura"}
CAPAS_CRITICAS = CAPAS_PRINCIPALES


@dataclass(frozen=True)
class Hallazgo:
    severidad: str
    categoria: str
    regla: str
    archivo: str
    linea: int
    detalle: str


@dataclass(frozen=True)
class DependenciaModulo:
    origen: str
    destino: str
    linea: int
    importacion: str
    archivo: str


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


def _es_entrypoint(relativo: str) -> bool:
    if relativo.endswith("/__main__.py"):
        return True
    return relativo.startswith("infraestructura/bootstrap/")


def _capa_de_archivo(relativo: str) -> str:
    partes = Path(relativo).parts
    if not partes:
        return ""
    return partes[0]


def _resolver_destino_import(capa_origen: str, nodo: ast.ImportFrom, relativo: str) -> str:
    if nodo.level == 0:
        return (nodo.module or "").split(".")[0]

    partes = list(Path(relativo).parts[:-1])
    subir = max(0, nodo.level - 1)
    if subir > len(partes):
        return ""

    base = partes[: len(partes) - subir]
    modulo_relativo = (nodo.module or "").split(".") if nodo.module else []
    full = [p for p in [*base, *modulo_relativo] if p]
    if not full:
        return capa_origen
    return full[0]


def _extraer_dependencias(raiz: Path, archivo: Path, arbol: ast.Module) -> list[DependenciaModulo]:
    relativo = archivo.relative_to(raiz).as_posix()
    capa_origen = _capa_de_archivo(relativo)
    deps: list[DependenciaModulo] = []

    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                destino = alias.name.split(".")[0]
                deps.append(DependenciaModulo(capa_origen, destino, nodo.lineno, alias.name, relativo))
        elif isinstance(nodo, ast.ImportFrom):
            destino = _resolver_destino_import(capa_origen, nodo, relativo)
            deps.append(DependenciaModulo(capa_origen, destino, nodo.lineno, nodo.module or "", relativo))

    return deps


def _analizar_imports_prohibidos(relativo: str, deps: list[DependenciaModulo]) -> list[Hallazgo]:
    hallazgos: list[Hallazgo] = []
    capa = _capa_de_archivo(relativo)
    for dep in deps:
        destino = dep.destino
        if capa == "presentacion" and destino == "dominio":
            hallazgos.append(Hallazgo("ALTO", "Capas", "Import prohibido presentacion->dominio", relativo, dep.linea, dep.importacion))
        if capa == "aplicacion" and destino == "infraestructura":
            hallazgos.append(Hallazgo("ALTO", "Capas", "Import prohibido aplicacion->infraestructura", relativo, dep.linea, dep.importacion))
        if capa == "dominio" and destino in {"aplicacion", "presentacion", "infraestructura"}:
            hallazgos.append(Hallazgo("ALTO", "Capas", "Import prohibido dominio->otras_capas", relativo, dep.linea, dep.importacion))
        if capa == "infraestructura" and destino == "presentacion":
            hallazgos.append(Hallazgo("ALTO", "Capas", "Import prohibido infraestructura->presentacion", relativo, dep.linea, dep.importacion))
    return hallazgos


def _analizar_privados(raiz: Path, archivo: Path, texto: str) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []
    for numero, linea in enumerate(texto.splitlines(), start=1):
        encadenado = PATRON_PRIVADOS_ENCADENADOS.search(linea)
        if encadenado:
            hallazgos.append(Hallazgo("ALTO", "Encapsulación", "Acceso encadenado a privados", relativo, numero, encadenado.group(0)))

    return hallazgos


def _analizar_metodos(raiz: Path, archivo: Path, arbol: ast.Module) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []

    for nodo in ast.walk(arbol):
        if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not hasattr(nodo, "end_lineno"):
            continue
        lineas = int(nodo.end_lineno) - int(nodo.lineno) + 1
        contador = _ContadorRamas()
        contador.visit(nodo)
        ramas = contador.ramas

        if lineas > 100:
            hallazgos.append(Hallazgo("ALTO", "Complejidad", "Método > 100 líneas", relativo, nodo.lineno, f"{nodo.name}: lineas={lineas}"))
        elif lineas > 80:
            hallazgos.append(Hallazgo("MEDIO", "Complejidad", "Método > 80 líneas", relativo, nodo.lineno, f"{nodo.name}: lineas={lineas}"))

        if ramas > 8:
            hallazgos.append(Hallazgo("ALTO", "Complejidad", "Método con ramas > 8", relativo, nodo.lineno, f"{nodo.name}: ramas={ramas}"))
        elif 6 <= ramas <= 8:
            hallazgos.append(Hallazgo("MEDIO", "Complejidad", "Método con ramas entre 6 y 8", relativo, nodo.lineno, f"{nodo.name}: ramas={ramas}"))

    return hallazgos


def _analizar_excepts_y_raise(raiz: Path, archivo: Path, arbol: ast.Module) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []

    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Try):
            continue

        for handler in nodo.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id == "Exception" and not _es_entrypoint(relativo):
                hallazgos.append(
                    Hallazgo("ALTO", "Manejo de errores", "except Exception fuera de entrypoint", relativo, handler.lineno, "except Exception")
                )

            nombre_alias = handler.name if isinstance(handler.name, str) else None
            if not nombre_alias:
                continue
            for interno in ast.walk(handler):
                if not isinstance(interno, ast.Raise):
                    continue
                if interno.exc is None:
                    continue
                if interno.cause is None:
                    hallazgos.append(
                        Hallazgo("MEDIO", "Manejo de errores", "raise sin preservar causa", relativo, interno.lineno, f"Falta 'from {nombre_alias}'")
                    )
                elif isinstance(interno.cause, ast.Name) and interno.cause.id != nombre_alias:
                    hallazgos.append(
                        Hallazgo(
                            "BAJO",
                            "Manejo de errores",
                            "raise from alias distinto",
                            relativo,
                            interno.lineno,
                            f"Alias esperado={nombre_alias}, actual={interno.cause.id}",
                        )
                    )

    return hallazgos


def _analizar_cohesion(raiz: Path, archivo: Path, texto: str, arbol: ast.Module) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []

    loc = len(texto.splitlines())
    if _capa_de_archivo(relativo) in CAPAS_CRITICAS:
        if loc > 550:
            hallazgos.append(Hallazgo("ALTO", "Cohesión", "Archivo > 550 LOC", relativo, 1, f"LOC={loc}"))
        elif loc > 450:
            hallazgos.append(Hallazgo("MEDIO", "Cohesión", "Archivo > 450 LOC", relativo, 1, f"LOC={loc}"))

    clases_publicas = [n for n in arbol.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
    if len(clases_publicas) > 6:
        hallazgos.append(
            Hallazgo("MEDIO", "Cohesión", "Archivo con más de 6 clases públicas", relativo, 1, f"clases_publicas={len(clases_publicas)}")
        )

    return hallazgos


def _detectar_ciclos_por_capa(deps: list[DependenciaModulo]) -> list[Hallazgo]:
    grafo: dict[str, set[str]] = {capa: set() for capa in CAPAS_PRINCIPALES}
    for dep in deps:
        if dep.origen in CAPAS_PRINCIPALES and dep.destino in CAPAS_PRINCIPALES and dep.origen != dep.destino:
            grafo[dep.origen].add(dep.destino)

    hallazgos: list[Hallazgo] = []

    def _dfs(origen: str, actual: str, visitados: list[str]) -> None:
        for vecino in grafo.get(actual, set()):
            if vecino == origen and len(visitados) >= 2:
                ruta = "->".join([*visitados, vecino])
                hallazgos.append(Hallazgo("ALTO", "Capas", "Ciclo entre capas", "(global)", 1, ruta))
                continue
            if vecino in visitados:
                continue
            _dfs(origen, vecino, [*visitados, vecino])

    for capa in CAPAS_PRINCIPALES:
        _dfs(capa, capa, [capa])

    unicos: list[Hallazgo] = []
    vistos: set[str] = set()
    for hallazgo in hallazgos:
        if hallazgo.detalle in vistos:
            continue
        vistos.add(hallazgo.detalle)
        unicos.append(hallazgo)
    return unicos


def _analizar_framework_validacion(raiz: Path, archivo: Path, arbol: ast.Module, deps: list[DependenciaModulo]) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    if not relativo.startswith("aplicacion/validacion/"):
        return []

    hallazgos: list[Hallazgo] = []

    for nodo in arbol.body:
        if isinstance(nodo, ast.ClassDef) and nodo.name.endswith("Regla"):
            if hasattr(nodo, "end_lineno"):
                lineas = int(nodo.end_lineno) - int(nodo.lineno) + 1
                if lineas >= 30:
                    hallazgos.append(Hallazgo("MEDIO", "Validación", "Regla de validación extensa", relativo, nodo.lineno, f"{nodo.name}: lineas={lineas}"))

    if relativo == "aplicacion/validacion/motor_validacion.py":
        for dep in deps:
            if dep.destino in {"presentacion", "infraestructura", "dominio"}:
                hallazgos.append(
                    Hallazgo("ALTO", "Validación", "MotorValidacion con acoplamiento indebido", relativo, dep.linea, dep.importacion)
                )

    return hallazgos


def _analizar_logica_negocio_en_infraestructura(raiz: Path, archivo: Path, arbol: ast.Module) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    if not relativo.startswith("infraestructura/"):
        return []

    hallazgos: list[Hallazgo] = []
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        nombre = nodo.name.lower()
        if any(token in nombre for token in {"regla", "negocio", "validar_dominio"}):
            hallazgos.append(
                Hallazgo("MEDIO", "Validación", "Posible lógica de negocio en infraestructura", relativo, nodo.lineno, nodo.name)
            )
    return hallazgos


def _analizar_concurrencia(raiz: Path, archivo: Path, arbol: ast.Module, texto: str) -> list[Hallazgo]:
    relativo = archivo.relative_to(raiz).as_posix()
    hallazgos: list[Hallazgo] = []

    if relativo.startswith("presentacion/") and "trabajador" not in relativo:
        if "subprocess." in texto or "time.sleep(" in texto:
            hallazgos.append(
                Hallazgo("MEDIO", "Concurrencia", "Posible operación pesada en hilo UI", relativo, 1, "subprocess/time.sleep en presentación")
            )

    if relativo.startswith("presentacion/trabajadores/"):
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Try):
                continue
            if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name) and nodo.func.id == "run":
                hallazgos.append(
                    Hallazgo("BAJO", "Concurrencia", "Trabajador podría bloquear hilo principal", relativo, nodo.lineno, "Revisar uso de run")
                )

    return hallazgos


def auditar_diseno_cohesion_v5(raiz: Path) -> dict[str, Any]:
    hallazgos: list[Hallazgo] = []
    dependencias_globales: list[DependenciaModulo] = []

    for archivo in _iterar_archivos_python(raiz):
        relativo = archivo.relative_to(raiz).as_posix()
        texto = archivo.read_text(encoding="utf-8")
        try:
            arbol = ast.parse(texto)
        except SyntaxError as exc:
            LOGGER.warning("No se pudo parsear %s: %s", relativo, exc)
            continue

        deps = _extraer_dependencias(raiz, archivo, arbol)
        dependencias_globales.extend(deps)
        hallazgos.extend(_analizar_imports_prohibidos(relativo, deps))
        hallazgos.extend(_analizar_privados(raiz, archivo, texto))
        hallazgos.extend(_analizar_metodos(raiz, archivo, arbol))
        hallazgos.extend(_analizar_excepts_y_raise(raiz, archivo, arbol))
        hallazgos.extend(_analizar_cohesion(raiz, archivo, texto, arbol))
        hallazgos.extend(_analizar_framework_validacion(raiz, archivo, arbol, deps))
        hallazgos.extend(_analizar_logica_negocio_en_infraestructura(raiz, archivo, arbol))
        hallazgos.extend(_analizar_concurrencia(raiz, archivo, arbol, texto))

    hallazgos.extend(_detectar_ciclos_por_capa(dependencias_globales))

    ordenados = sorted(hallazgos, key=lambda h: (SEVERIDAD_ORDEN.get(h.severidad, 9), h.archivo, h.linea, h.regla, h.detalle))
    resumen = {
        "ALTO": len([h for h in ordenados if h.severidad == "ALTO"]),
        "MEDIO": len([h for h in ordenados if h.severidad == "MEDIO"]),
        "BAJO": len([h for h in ordenados if h.severidad == "BAJO"]),
    }
    nota = max(0.0, min(10.0, round(10.0 - resumen["ALTO"] * 1.5 - resumen["MEDIO"] * 0.03 - resumen["BAJO"] * 0.01, 2)))

    return {
        "hallazgos": [asdict(h) for h in ordenados],
        "resumen": {
            **resumen,
            "nota_final": nota,
            "arquitectura_sin_altos": resumen["ALTO"] == 0,
        },
    }


def _parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audita diseño/cohesión v5 del repositorio")
    parser.add_argument("--raiz", type=Path, default=Path(__file__).resolve().parents[1], help="Ruta del repositorio")
    parser.add_argument("--salida", type=Path, required=True, help="Ruta de salida JSON")
    parser.add_argument("--debug", action="store_true", help="Activa logging DEBUG")
    return parser.parse_args()


def main() -> int:
    args = _parsear_argumentos()
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    resultado = auditar_diseno_cohesion_v5(args.raiz.resolve())
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    LOGGER.info("Auditoría v5 escrita en %s", args.salida)
    LOGGER.debug("Resumen v5: %s", resultado.get("resumen", {}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
