from __future__ import annotations

from pathlib import Path
import threading

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from dominio.modelos import EspecificacionClase, EspecificacionProyecto
from infraestructura.manifest.generador_manifest import GeneradorManifest
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal


def _generador() -> GenerarProyectoMvp:
    sistema = SistemaArchivosReal()
    return GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlan(sistema),
        sistema_archivos=sistema,
        generador_manifest=GeneradorManifest(),
    )


def _entrada(tmp_path: Path, nombre: str, blueprints: list[str]) -> GenerarProyectoMvpEntrada:
    espec = EspecificacionProyecto(nombre_proyecto=nombre, ruta_destino=str(tmp_path), version="1.0.0")
    espec.agregar_clase(EspecificacionClase(nombre="Cliente"))
    return GenerarProyectoMvpEntrada(especificacion_proyecto=espec, ruta_destino=str(tmp_path), nombre_proyecto=nombre, blueprints=blueprints)


def test_concurrencia_basica_dos_generaciones_no_comparten_estado(tmp_path: Path) -> None:
    resultados: dict[str, str] = {}

    def _run(nombre: str, blueprints: list[str]) -> None:
        salida = _generador().ejecutar(_entrada(tmp_path, nombre, blueprints))
        resultados[nombre] = salida.ruta_generada

    hilo_a = threading.Thread(target=_run, args=("concurrente_a", ["base_clean_arch_v1"]))
    hilo_b = threading.Thread(target=_run, args=("concurrente_b", ["base_clean_arch_v1", "crud_json_v1"]))
    hilo_a.start()
    hilo_b.start()
    hilo_a.join()
    hilo_b.join()

    assert Path(resultados["concurrente_a"]).name == "concurrente_a"
    assert Path(resultados["concurrente_b"]).name == "concurrente_b"
    assert Path(resultados["concurrente_a"]) != Path(resultados["concurrente_b"])
