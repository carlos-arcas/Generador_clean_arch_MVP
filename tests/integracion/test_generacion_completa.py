from __future__ import annotations

import json
import logging
from pathlib import Path

from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import GenerarProyectoMvp, GenerarProyectoMvpEntrada
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from infraestructura.logging_config import configurar_logging
from infraestructura.manifest.generador_manifest import GeneradorManifest
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal


def _crear_especificacion(ruta_base: Path, nombre_proyecto: str) -> EspecificacionProyecto:
    especificacion = EspecificacionProyecto(
        nombre_proyecto=nombre_proyecto,
        ruta_destino=str(ruta_base),
        descripcion="Integración completa",
        version="1.0.0",
    )
    clase = EspecificacionClase(nombre="Cliente")
    clase.agregar_atributo(EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True))
    especificacion.agregar_clase(clase)
    return especificacion


def _crear_generador() -> GenerarProyectoMvp:
    sistema = SistemaArchivosReal()
    return GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlan(sistema),
        sistema_archivos=sistema,
        generador_manifest=GeneradorManifest(),
    )


def test_generacion_completa_publica_manifest_y_escribe_logs_sin_print(tmp_path: Path, capsys) -> None:
    logs_dir = tmp_path / "logs"
    configurar_logging(str(logs_dir))

    caso_uso = _crear_generador()
    entrada = GenerarProyectoMvpEntrada(
        especificacion_proyecto=_crear_especificacion(tmp_path, "proyecto_ok"),
        ruta_destino=str(tmp_path),
        nombre_proyecto="proyecto_ok",
        blueprints=["base_clean_arch_v1", "crud_json_v1"],
    )

    salida = caso_uso.ejecutar(entrada)
    captured = capsys.readouterr()

    assert captured.out == ""
    assert captured.err == ""

    ruta_proyecto = Path(salida.ruta_generada)
    manifest = json.loads((ruta_proyecto / "configuracion" / "MANIFEST.json").read_text(encoding="utf-8"))

    assert manifest["blueprints"] == ["base_clean_arch_v1", "crud_json_v1"]
    assert manifest["archivos_generados"] > 0

    logging.getLogger("caso_uso_generacion").info("caso_uso=GenerarProyectoMvp ejecutado")
    seguimiento = (logs_dir / "seguimiento.log").read_text(encoding="utf-8")
    assert "INFO" in seguimiento
    assert "caso_uso=GenerarProyectoMvp" in seguimiento
