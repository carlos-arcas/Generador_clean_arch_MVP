"""Pruebas del caso de uso GenerarProyectoMvp."""

from __future__ import annotations

from pathlib import Path

from aplicacion.casos_uso.auditar_proyecto_generado import AuditarProyectoGenerado
from aplicacion.casos_uso.crear_plan_desde_blueprints import CrearPlanDesdeBlueprints
from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from aplicacion.casos_uso.generacion.generar_proyecto_mvp import (
    GenerarProyectoMvp,
    GenerarProyectoMvpEntrada,
)
from aplicacion.casos_uso.generar_manifest import GenerarManifest
from aplicacion.dtos.auditoria.dto_auditoria_entrada import DtoAuditoriaEntrada
from aplicacion.dtos.auditoria.dto_auditoria_salida import DtoAuditoriaSalida
from dominio.modelos import EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto
from infraestructura.calculadora_hash_real import CalculadoraHashReal
from infraestructura.repositorio_blueprints_en_disco import RepositorioBlueprintsEnDisco
from infraestructura.sistema_archivos_real import SistemaArchivosReal


class AuditorFalso(AuditarProyectoGenerado):
    def __init__(self) -> None:
        pass

    def ejecutar(self, entrada: DtoAuditoriaEntrada) -> DtoAuditoriaSalida:
        return DtoAuditoriaSalida(valido=True, lista_errores=[], warnings=[], cobertura=90.0, resumen="ok")


def test_generar_proyecto_mvp_crea_estructura_minima(tmp_path: Path) -> None:
    ruta_base = tmp_path
    ruta_proyecto = ruta_base / "proyecto_mvp"
    especificacion = EspecificacionProyecto(
        nombre_proyecto="proyecto_mvp",
        ruta_destino=str(ruta_base),
        descripcion="Proyecto MVP",
        version="1.0.0",
    )
    clase_cliente = EspecificacionClase(nombre="Cliente")
    clase_cliente.agregar_atributo(EspecificacionAtributo(nombre="nombre", tipo="str", obligatorio=True))
    clase_cliente.agregar_atributo(EspecificacionAtributo(nombre="edad", tipo="int", obligatorio=False))
    especificacion.agregar_clase(clase_cliente)

    generar_manifest = GenerarManifest(CalculadoraHashReal())
    sistema_archivos = SistemaArchivosReal()
    caso_uso = GenerarProyectoMvp(
        crear_plan_desde_blueprints=CrearPlanDesdeBlueprints(RepositorioBlueprintsEnDisco("blueprints")),
        ejecutar_plan=EjecutarPlan(sistema_archivos, generar_manifest),
        sistema_archivos=sistema_archivos,
        auditor=AuditorFalso(),
    )

    salida = caso_uso.ejecutar(
        GenerarProyectoMvpEntrada(
            especificacion_proyecto=especificacion,
            ruta_destino=str(ruta_base),
            nombre_proyecto="proyecto_mvp",
            blueprints=["base_clean_arch_v1", "crud_json_v1"],
        )
    )

    assert salida.valido is True
    assert salida.errores == []
    assert Path(salida.ruta_generada).exists()

    directorios_esperados = [
        "dominio",
        "aplicacion",
        "infraestructura",
        "presentacion",
        "tests",
        "scripts",
        "docs",
        "logs",
        "configuracion",
    ]
    for directorio in directorios_esperados:
        assert (ruta_proyecto / directorio).exists()

    assert (ruta_proyecto / "VERSION").exists()
    assert (ruta_proyecto / "README.md").exists()
    assert salida.archivos_generados > 0
