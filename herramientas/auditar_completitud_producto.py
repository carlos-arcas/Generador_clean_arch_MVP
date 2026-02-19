from __future__ import annotations

import ast
import logging
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

DIRECTORIOS_IGNORADOS = {".git", ".venv", "__pycache__", ".pytest_cache"}
SECCIONES_OBLIGATORIAS = {"A", "B", "C", "D", "E"}
PATRON_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass(frozen=True)
class Hallazgo:
    prioridad: str
    seccion: str
    descripcion: str
    accion: str
    ruta: str = "N/A"


@dataclass
class ResultadoSeccion:
    codigo: str
    titulo: str
    puntaje: float
    maximo: float
    estado: str
    evidencias: list[str] = field(default_factory=list)
    faltantes: list[Hallazgo] = field(default_factory=list)


@dataclass
class ResultadoAuditoria:
    ruta_repo: Path
    secciones: list[ResultadoSeccion]
    hallazgos: list[Hallazgo]
    prints_detectados: list[str]

    @property
    def puntaje_total(self) -> float:
        return round(sum(seccion.puntaje for seccion in self.secciones), 2)

    @property
    def puntaje_maximo(self) -> float:
        return round(sum(seccion.maximo for seccion in self.secciones), 2)

    @property
    def tiene_fallos_criticos(self) -> bool:
        for seccion in self.secciones:
            if seccion.codigo in SECCIONES_OBLIGATORIAS and seccion.estado == "FAIL":
                return True
        return False

    @property
    def codigo_salida(self) -> int:
        return 1 if self.tiene_fallos_criticos else 0


def _configurar_logger(ruta_repo: Path) -> logging.Logger:
    logger = logging.getLogger("auditor_completitud_producto")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    carpeta_logs = ruta_repo / "logs"
    if carpeta_logs.exists():
        seguimiento = carpeta_logs / "seguimiento.log"
        crashes = carpeta_logs / "crashes.log"
    else:
        temporal = Path(tempfile.gettempdir()) / "auditor_completitud_producto"
        temporal.mkdir(parents=True, exist_ok=True)
        seguimiento = temporal / "seguimiento.log"
        crashes = temporal / "crashes.log"

    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s")

    handler_info = logging.FileHandler(seguimiento, encoding="utf-8")
    handler_info.setLevel(logging.INFO)
    handler_info.setFormatter(formato)

    handler_error = logging.FileHandler(crashes, encoding="utf-8")
    handler_error.setLevel(logging.ERROR)
    handler_error.setFormatter(formato)

    logger.addHandler(handler_info)
    logger.addHandler(handler_error)
    return logger


def _iterar_archivos_python(ruta_repo: Path) -> Iterable[Path]:
    for archivo in ruta_repo.rglob("*.py"):
        relativa = archivo.relative_to(ruta_repo)
        if any(parte in DIRECTORIOS_IGNORADOS for parte in relativa.parts):
            continue
        yield archivo


def _leer_texto_seguro(archivo: Path) -> str:
    return archivo.read_text(encoding="utf-8")


def _modulo_desde_archivo(ruta_repo: Path, archivo: Path) -> str:
    relativa = archivo.relative_to(ruta_repo).with_suffix("")
    partes = list(relativa.parts)
    if partes and partes[-1] == "__init__":
        partes = partes[:-1]
    return ".".join(partes)


def _extraer_imports_locales(ruta_repo: Path, archivo: Path) -> set[str]:
    imports: set[str] = set()
    texto = _leer_texto_seguro(archivo)
    try:
        arbol = ast.parse(texto)
    except SyntaxError:
        return imports

    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for nombre in nodo.names:
                modulo = nombre.name
                if modulo.split(".")[0] in {
                    "dominio",
                    "aplicacion",
                    "infraestructura",
                    "presentacion",
                    "configuracion",
                    "scripts",
                    "herramientas",
                }:
                    imports.add(modulo)
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.module is None:
                continue
            modulo = nodo.module
            if modulo.split(".")[0] in {
                "dominio",
                "aplicacion",
                "infraestructura",
                "presentacion",
                "configuracion",
                "scripts",
                "herramientas",
            }:
                imports.add(modulo)
    return imports


def _detectar_ciclos(grafo: dict[str, set[str]]) -> list[list[str]]:
    visitados: set[str] = set()
    en_pila: set[str] = set()
    pila: list[str] = []
    ciclos: list[list[str]] = []

    def dfs(nodo: str) -> None:
        visitados.add(nodo)
        en_pila.add(nodo)
        pila.append(nodo)
        for vecino in grafo.get(nodo, set()):
            if vecino not in grafo:
                continue
            if vecino not in visitados:
                dfs(vecino)
            elif vecino in en_pila:
                inicio = pila.index(vecino)
                ciclo = pila[inicio:] + [vecino]
                if ciclo not in ciclos:
                    ciclos.append(ciclo)
        pila.pop()
        en_pila.remove(nodo)

    for nodo in grafo:
        if nodo not in visitados:
            dfs(nodo)
    return ciclos


def _evaluar_estructura(ruta_repo: Path) -> ResultadoSeccion:
    faltantes: list[Hallazgo] = []
    evidencias: list[str] = []
    puntaje = 10.0

    carpetas = [
        "dominio",
        "aplicacion",
        "infraestructura",
        "presentacion",
        "tests",
        "docs",
        "logs",
        "configuracion",
        "scripts",
    ]
    for carpeta in carpetas:
        existe = (ruta_repo / carpeta).exists()
        evidencias.append(f"Carpeta {carpeta}: {'OK' if existe else 'FALTA'}")
        if not existe:
            puntaje -= 1.0
            faltantes.append(
                Hallazgo("P0", "A", f"Falta carpeta obligatoria: {carpeta}", "Crear carpeta base", carpeta)
            )

    grafo: dict[str, set[str]] = {}
    for archivo in _iterar_archivos_python(ruta_repo):
        modulo = _modulo_desde_archivo(ruta_repo, archivo)
        if not modulo:
            continue
        grafo[modulo] = _extraer_imports_locales(ruta_repo, archivo)

    ciclos = _detectar_ciclos(grafo)
    evidencias.append(f"Ciclos detectados: {len(ciclos)}")
    if ciclos:
        puntaje -= 2.0
        faltantes.append(
            Hallazgo("P0", "A", "Se detectaron imports circulares", "Romper dependencias cíclicas", str(ciclos[0]))
        )

    for archivo in _iterar_archivos_python(ruta_repo):
        relativa = archivo.relative_to(ruta_repo).as_posix()
        texto = _leer_texto_seguro(archivo)
        for idx, linea in enumerate(texto.splitlines(), start=1):
            limpia = linea.strip()
            if not limpia.startswith(("import ", "from ")):
                continue
            if relativa.startswith("dominio/") and any(
                token in limpia
                for token in ("aplicacion", "infraestructura", "presentacion")
            ):
                puntaje -= 0.4
                faltantes.append(
                    Hallazgo(
                        "P0",
                        "A",
                        "Dominio depende de capas externas",
                        "Eliminar dependencia en dominio",
                        f"{relativa}:{idx}",
                    )
                )
            if relativa.startswith("aplicacion/") and any(
                token in limpia for token in ("infraestructura", "presentacion")
            ):
                puntaje -= 0.4
                faltantes.append(
                    Hallazgo(
                        "P0",
                        "A",
                        "Aplicación depende de infraestructura/presentación",
                        "Usar puertos e inversión de dependencias",
                        f"{relativa}:{idx}",
                    )
                )
            if relativa.startswith("presentacion/") and "infraestructura" in limpia and "bootstrap" not in limpia:
                puntaje -= 0.3
                faltantes.append(
                    Hallazgo(
                        "P1",
                        "A",
                        "Presentación importa infraestructura directa",
                        "Mover al composition root o documentar excepción",
                        f"{relativa}:{idx}",
                    )
                )

    puntaje = max(0.0, round(puntaje, 2))
    estado = "PASS" if not any(h.prioridad == "P0" for h in faltantes) else "FAIL"
    return ResultadoSeccion("A", "Estructura y Clean Architecture", puntaje, 10.0, estado, evidencias, faltantes)


def _evaluar_testing(ruta_repo: Path) -> ResultadoSeccion:
    faltantes: list[Hallazgo] = []
    evidencias: list[str] = []
    puntaje = 10.0

    pytest_ok = (ruta_repo / "pytest.ini").exists() or (ruta_repo / "pyproject.toml").exists()
    evidencias.append(f"Configuración pytest: {'OK' if pytest_ok else 'FALTA'}")
    if not pytest_ok:
        puntaje -= 1.5
        faltantes.append(Hallazgo("P0", "B", "No hay configuración de pytest", "Agregar pytest.ini", "pytest.ini"))

    for capa in ("dominio", "aplicacion", "infraestructura", "presentacion"):
        existe = (ruta_repo / "tests" / capa).exists()
        evidencias.append(f"Tests capa {capa}: {'OK' if existe else 'FALTA'}")
        if not existe:
            puntaje -= 1.0
            faltantes.append(
                Hallazgo("P0", "B", f"Falta tests/{capa}", "Agregar tests por capa", f"tests/{capa}")
            )

    integracion = (ruta_repo / "tests" / "integracion").exists()
    snapshots = (ruta_repo / "tests" / "snapshots").exists()
    golden = (ruta_repo / "tests" / "snapshots" / "golden").exists()
    evidencias.extend(
        [
            f"tests/integracion: {'OK' if integracion else 'FALTA'}",
            f"tests/snapshots: {'OK' if snapshots else 'FALTA'}",
            f"tests/snapshots/golden: {'OK' if golden else 'FALTA'}",
        ]
    )
    if not integracion:
        puntaje -= 1.0
        faltantes.append(Hallazgo("P1", "B", "Falta carpeta de integración", "Crear tests/integracion", "tests/integracion"))
    if not snapshots or not golden:
        puntaje -= 1.0
        faltantes.append(Hallazgo("P1", "B", "Falta estrategia snapshots/golden", "Crear carpetas snapshots/golden", "tests/snapshots/golden"))

    docs_pruebas = (ruta_repo / "docs" / "guia_pruebas.md")
    script_tests = (ruta_repo / "scripts" / "ejecutar_tests.bat")
    cobertura_mencionada = False
    if docs_pruebas.exists() and "cov" in _leer_texto_seguro(docs_pruebas).lower():
        cobertura_mencionada = True
    if script_tests.exists() and "--cov" in _leer_texto_seguro(script_tests).lower():
        cobertura_mencionada = True
    evidencias.append(f"Cobertura documentada/configurada: {'OK' if cobertura_mencionada else 'FALTA'}")
    if not cobertura_mencionada:
        puntaje -= 1.0
        faltantes.append(Hallazgo("P1", "B", "No hay evidencia de cobertura", "Documentar y agregar comando --cov", "docs/guia_pruebas.md"))

    pruebas_texto = "\n".join(_leer_texto_seguro(p) for p in (ruta_repo / "tests").rglob("test_*.py")) if (ruta_repo / "tests").exists() else ""
    for carpeta in ("dominio", "aplicacion"):
        for archivo in (ruta_repo / carpeta).rglob("*.py"):
            if archivo.name == "__init__.py":
                continue
            texto = _leer_texto_seguro(archivo)
            if not re.search(r"^\s*(def|class)\s+[A-Za-z]", texto, flags=re.MULTILINE):
                continue
            modulo = _modulo_desde_archivo(ruta_repo, archivo)
            nombre = archivo.stem
            if modulo not in pruebas_texto and nombre not in pruebas_texto:
                puntaje -= 0.3
                faltantes.append(
                    Hallazgo("P2", "B", "Módulo público sin referencia en tests", "Agregar test que importe o mencione el módulo", modulo)
                )

    puntaje = max(0.0, round(puntaje, 2))
    estado = "PASS" if not any(h.prioridad == "P0" for h in faltantes) else "FAIL"
    return ResultadoSeccion("B", "Testing y Cobertura", puntaje, 10.0, estado, evidencias, faltantes)


def _evaluar_scripts_windows(ruta_repo: Path) -> ResultadoSeccion:
    faltantes: list[Hallazgo] = []
    evidencias: list[str] = []
    puntaje = 10.0

    lanzar = ruta_repo / "scripts" / "lanzar_app.bat"
    tests = ruta_repo / "scripts" / "ejecutar_tests.bat"

    def validar_patrones(archivo: Path, patrones: list[str], seccion: str) -> None:
        nonlocal puntaje
        if not archivo.exists():
            puntaje -= 5.0
            faltantes.append(Hallazgo("P0", seccion, f"Falta script {archivo.name}", "Crear script reproducible", archivo.as_posix()))
            evidencias.append(f"{archivo.name}: FALTA")
            return
        texto = _leer_texto_seguro(archivo).lower()
        evidencias.append(f"{archivo.name}: OK")
        for patron in patrones:
            if patron not in texto:
                puntaje -= 1.0
                faltantes.append(Hallazgo("P0", seccion, f"Script sin patrón requerido: {patron}", "Completar script .bat", archivo.as_posix()))

    validar_patrones(lanzar, [".venv", "requirements.txt", "python -m"], "C")
    validar_patrones(
        tests,
        [
            ".venv",
            "requirements.txt",
            "pytest -q --maxfail=1",
            "--cov=.",
            "--cov-fail-under=85",
            "todo ok",
            "fallos en tests",
        ],
        "C",
    )
    if tests.exists():
        texto_tests = _leer_texto_seguro(tests).lower()
        if "exit /b" not in texto_tests and "errorlevel" not in texto_tests:
            puntaje -= 1.0
            faltantes.append(Hallazgo("P0", "C", "Script de tests no devuelve errorlevel claro", "Agregar control de exit /b", tests.as_posix()))

    puntaje = max(0.0, round(puntaje, 2))
    estado = "PASS" if not any(h.prioridad == "P0" for h in faltantes) else "FAIL"
    return ResultadoSeccion("C", "Scripts reproducibles Windows", puntaje, 10.0, estado, evidencias, faltantes)


def _evaluar_logging(ruta_repo: Path) -> tuple[ResultadoSeccion, list[str]]:
    faltantes: list[Hallazgo] = []
    evidencias: list[str] = []
    puntaje = 10.0

    logs_ok = (ruta_repo / "logs" / "seguimiento.log").exists() and (ruta_repo / "logs" / "crashes.log").exists()
    evidencias.append(f"Archivos logs esperados: {'OK' if logs_ok else 'FALTA'}")
    if not logs_ok:
        puntaje -= 2.0
        faltantes.append(Hallazgo("P0", "D", "Faltan logs/seguimiento.log o logs/crashes.log", "Crear archivos de logging", "logs/"))

    tiene_rotacion = False
    tiene_formato = False
    tiene_excepthook = False
    for archivo in _iterar_archivos_python(ruta_repo):
        texto = _leer_texto_seguro(archivo)
        if "RotatingFileHandler" in texto or "TimedRotatingFileHandler" in texto:
            tiene_rotacion = True
        if "%(asctime)s" in texto and "%(levelname)s" in texto and "%(message)s" in texto:
            tiene_formato = True
        if "sys.excepthook" in texto:
            tiene_excepthook = True

    evidencias.extend(
        [
            f"Rotación de logs: {'OK' if tiene_rotacion else 'FALTA'}",
            f"Formato de logs estructurado: {'OK' if tiene_formato else 'FALTA'}",
            f"Captura global de excepciones: {'OK' if tiene_excepthook else 'FALTA'}",
        ]
    )
    if not tiene_rotacion:
        puntaje -= 2.0
        faltantes.append(Hallazgo("P0", "D", "No se detecta rotación de logs", "Agregar RotatingFileHandler", "infraestructura/logging_config.py"))
    if not tiene_formato:
        puntaje -= 1.0
        faltantes.append(Hallazgo("P1", "D", "No se detecta formato completo de logging", "Usar formato timestamp|nivel|módulo|función|mensaje", "infraestructura/logging_config.py"))
    if not tiene_excepthook:
        puntaje -= 2.0
        faltantes.append(Hallazgo("P0", "D", "No se detecta captura global de excepciones", "Configurar sys.excepthook", "presentacion/__main__.py"))

    prints_detectados: list[str] = []
    for archivo in _iterar_archivos_python(ruta_repo):
        relativa = archivo.relative_to(ruta_repo).as_posix()
        texto = _leer_texto_seguro(archivo)
        lineas = texto.splitlines()
        try:
            arbol = ast.parse(texto)
        except SyntaxError:
            continue
        for nodo in ast.walk(arbol):
            if not isinstance(nodo, ast.Call):
                continue
            if isinstance(nodo.func, ast.Name) and nodo.func.id == "print":
                numero = int(getattr(nodo, "lineno", 1))
                contenido = lineas[numero - 1].strip() if numero - 1 < len(lineas) else "print(...)"
                prints_detectados.append(f"{relativa}:{numero}: {contenido}")
    evidencias.append(f"print( detectados: {len(prints_detectados)}")
    if prints_detectados:
        puntaje -= min(3.0, 0.1 * len(prints_detectados))
        faltantes.append(Hallazgo("P1", "D", "Uso de print detectado", "Reemplazar print por logging", prints_detectados[0]))

    puntaje = max(0.0, round(puntaje, 2))
    estado = "PASS" if not any(h.prioridad == "P0" for h in faltantes) else "FAIL"
    return (
        ResultadoSeccion("D", "Observabilidad / Logging", puntaje, 10.0, estado, evidencias, faltantes),
        prints_detectados,
    )


def _evaluar_documentacion(ruta_repo: Path) -> ResultadoSeccion:
    faltantes: list[Hallazgo] = []
    evidencias: list[str] = []
    puntaje = 10.0

    docs_requeridos = [
        "README.md",
        "arquitectura.md",
        "decisiones_tecnicas.md",
        "guia_pruebas.md",
        "guia_logging.md",
    ]
    for nombre in docs_requeridos:
        existe = (ruta_repo / "docs" / nombre).exists()
        evidencias.append(f"docs/{nombre}: {'OK' if existe else 'FALTA'}")
        if not existe:
            puntaje -= 1.2
            faltantes.append(Hallazgo("P0", "E", f"Falta docs/{nombre}", "Crear documentación obligatoria", f"docs/{nombre}"))

    informe = ruta_repo / "docs" / "auditoria_completitud_producto.md"
    evidencias.append(
        "docs/auditoria_completitud_producto.md: OK"
        if informe.exists()
        else "docs/auditoria_completitud_producto.md: se genera al ejecutar este auditor"
    )

    arquitectura = ruta_repo / "docs" / "arquitectura.md"
    if arquitectura.exists():
        contenido = _leer_texto_seguro(arquitectura).lower()
        if "|" not in contenido and "---" not in contenido and "->" not in contenido:
            puntaje -= 1.0
            faltantes.append(Hallazgo("P1", "E", "arquitectura.md sin diagrama ASCII evidente", "Agregar diagrama y reglas", arquitectura.as_posix()))

    version = ruta_repo / "VERSION"
    if not version.exists() or not PATRON_SEMVER.match(_leer_texto_seguro(version).strip() if version.exists() else ""):
        puntaje -= 1.0
        faltantes.append(Hallazgo("P0", "E", "VERSION ausente o no semver", "Definir versión semver", "VERSION"))
        evidencias.append("VERSION semver: FALTA")
    else:
        evidencias.append("VERSION semver: OK")

    changelog = ruta_repo / "CHANGELOG.md"
    if not changelog.exists() or "##" not in (_leer_texto_seguro(changelog) if changelog.exists() else ""):
        puntaje -= 1.0
        faltantes.append(Hallazgo("P1", "E", "CHANGELOG sin formato esperado", "Agregar secciones con encabezados ##", "CHANGELOG.md"))
    evidencias.append(f"CHANGELOG.md: {'OK' if changelog.exists() else 'FALTA'}")

    puntaje = max(0.0, round(puntaje, 2))
    estado = "PASS" if not any(h.prioridad == "P0" for h in faltantes) else "FAIL"
    return ResultadoSeccion("E", "Documentación", puntaje, 10.0, estado, evidencias, faltantes)


def _evaluar_ux_minima(ruta_repo: Path) -> ResultadoSeccion:
    faltantes: list[Hallazgo] = []
    evidencias: list[str] = []
    puntaje = 10.0

    archivo_mapeo = ruta_repo / "presentacion" / "mapeo_mensajes_error.py"
    if archivo_mapeo.exists():
        evidencias.append("Mapeo de errores a UX: OK")
    else:
        puntaje -= 3.0
        evidencias.append("Mapeo de errores a UX: FALTA")
        faltantes.append(Hallazgo("P1", "F", "No se encontró mapeo de mensajes de error", "Crear presentacion/mapeo_mensajes_error.py", "presentacion/mapeo_mensajes_error.py"))

    patrones_genericos = ["falló mvp", "error inesperado", "algo salió mal", "ha ocurrido un error"]
    hallazgos_genericos: list[str] = []
    for archivo in _iterar_archivos_python(ruta_repo):
        relativa = archivo.relative_to(ruta_repo).as_posix()
        texto = _leer_texto_seguro(archivo).lower()
        for patron in patrones_genericos:
            if patron in texto:
                hallazgos_genericos.append(f"{relativa} contiene '{patron}'")

    evidencias.append(f"Mensajes genéricos detectados: {len(hallazgos_genericos)}")
    if hallazgos_genericos:
        puntaje -= min(4.0, len(hallazgos_genericos) * 1.0)
        faltantes.append(Hallazgo("P1", "F", "Mensajes de error genéricos detectados", "Agregar códigos y causa accionable para usuario", hallazgos_genericos[0]))

    faltantes.extend(
        [
            Hallazgo("P2", "F", "Recomendación UX: ID de incidente por operación", "Agregar correlación de incidente en pantalla", "presentacion/"),
            Hallazgo("P2", "F", "Recomendación UX: botón copiar detalles/abrir logs", "Agregar acciones de soporte en UI", "presentacion/"),
            Hallazgo("P2", "F", "Recomendación UX: estado cargando y re-habilitar botones", "Controlar estado durante operaciones", "presentacion/"),
        ]
    )

    puntaje = max(0.0, round(puntaje, 2))
    estado = "PASS" if puntaje >= 7.0 else "FAIL"
    return ResultadoSeccion("F", "UX mínima de producto", puntaje, 10.0, estado, evidencias, faltantes)


def auditar_completitud_producto(ruta_repo: Path) -> ResultadoAuditoria:
    logger = _configurar_logger(ruta_repo)
    logger.info("Iniciando auditoría de completitud en %s", ruta_repo)

    seccion_a = _evaluar_estructura(ruta_repo)
    seccion_b = _evaluar_testing(ruta_repo)
    seccion_c = _evaluar_scripts_windows(ruta_repo)
    seccion_d, prints_detectados = _evaluar_logging(ruta_repo)
    seccion_e = _evaluar_documentacion(ruta_repo)
    seccion_f = _evaluar_ux_minima(ruta_repo)

    secciones = [seccion_a, seccion_b, seccion_c, seccion_d, seccion_e, seccion_f]
    hallazgos = [hallazgo for seccion in secciones for hallazgo in seccion.faltantes]

    logger.info("Auditoría completada. Puntaje total: %.2f/%.2f", sum(s.puntaje for s in secciones), sum(s.maximo for s in secciones))
    return ResultadoAuditoria(ruta_repo=ruta_repo, secciones=secciones, hallazgos=hallazgos, prints_detectados=prints_detectados)


def _renderizar_informe(resultado: ResultadoAuditoria) -> str:
    lineas: list[str] = []
    porcentaje = (resultado.puntaje_total / resultado.puntaje_maximo) * 100 if resultado.puntaje_maximo else 0
    estado_global = "APROBADO" if resultado.codigo_salida == 0 else "CON FALLOS CRÍTICOS"

    lineas.append("# Auditoría de completitud del producto")
    lineas.append("")
    lineas.append("## 1) Resumen ejecutivo")
    lineas.append(f"- Estado general: **{estado_global}**.")
    lineas.append(f"- Puntaje total: **{resultado.puntaje_total:.2f}/{resultado.puntaje_maximo:.2f} ({porcentaje:.1f}%)**.")
    lineas.append(f"- Fallos críticos: **{'Sí' if resultado.tiene_fallos_criticos else 'No'}**.")
    lineas.append("")

    lineas.append("## 2) Tabla de puntuación por sección")
    lineas.append("| Sección | Puntaje | Estado |")
    lineas.append("|---|---:|---|")
    for seccion in resultado.secciones:
        lineas.append(f"| {seccion.codigo} - {seccion.titulo} | {seccion.puntaje:.2f}/10 | {seccion.estado} |")
    lineas.append("")

    lineas.append("## 3) Lista priorizada de faltantes (P0/P1/P2)")
    if not resultado.hallazgos:
        lineas.append("- Sin faltantes detectados.")
    else:
        for prioridad in ("P0", "P1", "P2"):
            seleccionados = [h for h in resultado.hallazgos if h.prioridad == prioridad]
            if not seleccionados:
                continue
            lineas.append(f"### {prioridad}")
            for hallazgo in seleccionados:
                lineas.append(f"- [{hallazgo.seccion}] {hallazgo.descripcion} | Acción: {hallazgo.accion} | Ruta: `{hallazgo.ruta}`")
    lineas.append("")

    lineas.append("## 4) Evidencias")
    for seccion in resultado.secciones:
        lineas.append(f"### {seccion.codigo} - {seccion.titulo}")
        for evidencia in seccion.evidencias:
            lineas.append(f"- {evidencia}")
    lineas.append("### Lista de prints detectados")
    if resultado.prints_detectados:
        for item in resultado.prints_detectados:
            lineas.append(f"- {item}")
    else:
        lineas.append("- No se detectaron usos de print(.")
    lineas.append("")

    lineas.append("## 5) Comandos recomendados")
    lineas.append("- `python -m presentacion`")
    lineas.append("- `scripts\\lanzar_app.bat`")
    lineas.append("- `scripts\\ejecutar_tests.bat`")
    lineas.append("- `pytest -q --maxfail=1`")
    lineas.append("")

    lineas.append("## 6) Definición de DONE para 100%")
    lineas.append("- [ ] Secciones A-E en PASS y sin faltantes P0.")
    lineas.append("- [ ] Cobertura configurada y umbral >= 85% en scripts y guía.")
    lineas.append("- [ ] Logging con rotación, crashes y captura global de excepciones.")
    lineas.append("- [ ] Sin `print(` en código de producción.")
    lineas.append("- [ ] UX mínima con mapeo de errores y mensajes accionables.")

    return "\n".join(lineas) + "\n"


def _resolver_raiz_repo() -> Path:
    actual = Path.cwd().resolve()
    for candidato in [actual, *actual.parents]:
        if (candidato / ".git").exists():
            return candidato
    return actual


def main() -> int:
    ruta_repo = _resolver_raiz_repo()
    logger = _configurar_logger(ruta_repo)
    try:
        resultado = auditar_completitud_producto(ruta_repo)
        carpeta_docs = ruta_repo / "docs"
        carpeta_docs.mkdir(parents=True, exist_ok=True)
        ruta_informe = carpeta_docs / "auditoria_completitud_producto.md"
        ruta_informe.write_text(_renderizar_informe(resultado), encoding="utf-8")
        logger.info("Informe escrito en %s", ruta_informe)
        return resultado.codigo_salida
    except Exception:
        logger.exception("Error no controlado en la auditoría")
        return 2


if __name__ == "__main__":
    sys.exit(main())
