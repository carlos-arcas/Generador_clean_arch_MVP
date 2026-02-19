from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from aplicacion.casos_uso.auditoria.auditar_proyecto_generado import ResultadoAuditoria
from aplicacion.casos_uso.generacion.pasos.ejecutar_auditoria import EjecutorAuditoriaGeneracion
from aplicacion.casos_uso.generacion.pasos.normalizar_entrada import NormalizadorEntradaGeneracion
from aplicacion.casos_uso.generacion.pasos.rollback_generacion import RollbackGeneracion
from aplicacion.casos_uso.generacion.pasos.validar_entrada import ValidadorEntradaGeneracion
from aplicacion.errores.errores_pipeline import ErrorAuditoriaGeneracion, ErrorValidacionEntradaGeneracion
from dominio.especificacion import EspecificacionProyecto


@dataclass
class _Entrada:
    especificacion_proyecto: EspecificacionProyecto
    ruta_destino: str
    nombre_proyecto: str
    blueprints: list[str]


class _AuditorOk:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        return ResultadoAuditoria(errores=[], warnings=[])


class _AuditorFalla:
    def auditar(self, ruta_proyecto: str) -> ResultadoAuditoria:
        raise RuntimeError(f"fallo en {ruta_proyecto}")


def _entrada_minima(tmp_path: Path) -> _Entrada:
    return _Entrada(
        especificacion_proyecto=EspecificacionProyecto(nombre_proyecto="Demo", ruta_destino=str(tmp_path)),
        ruta_destino=str(tmp_path),
        nombre_proyecto="Demo",
        blueprints=["base_clean_arch_v1", "crud_json"],
    )


def test_normalizar_entrada_caso_minimo_y_borde_blueprints(tmp_path: Path) -> None:
    entrada = _entrada_minima(tmp_path)
    ruta_proyecto = tmp_path / "Demo"

    normalizada = NormalizadorEntradaGeneracion().normalizar(entrada, ruta_proyecto)

    assert normalizada.ruta_proyecto == str(ruta_proyecto)
    assert normalizada.blueprints == ["base_clean_arch", "crud_json"]
    assert normalizada.especificacion_proyecto.ruta_destino == str(ruta_proyecto)


def test_validar_entrada_invalida_lanza_error_esperado(tmp_path: Path) -> None:
    entrada_invalida = _Entrada(
        especificacion_proyecto=EspecificacionProyecto(nombre_proyecto="Demo", ruta_destino=str(tmp_path)),
        ruta_destino=str(tmp_path),
        nombre_proyecto=" ",
        blueprints=[],
    )

    with pytest.raises(ErrorValidacionEntradaGeneracion, match="nombre del proyecto"):
        ValidadorEntradaGeneracion().validar(entrada_invalida)


def test_rollback_generacion_elimina_carpeta_creada(tmp_path: Path) -> None:
    ruta = tmp_path / "proyecto"
    ruta.mkdir()
    (ruta / "archivo.txt").write_text("contenido", encoding="utf-8")

    se_elimino = RollbackGeneracion().ejecutar(ruta, carpeta_creada_en_ejecucion=True)

    assert se_elimino is True
    assert not ruta.exists()


def test_ejecutar_auditoria_reacciona_ok_y_fail() -> None:
    resultado = EjecutorAuditoriaGeneracion(_AuditorOk()).ejecutar("/tmp/demo")

    assert resultado.valido is True

    with pytest.raises(ErrorAuditoriaGeneracion):
        EjecutorAuditoriaGeneracion(_AuditorFalla()).ejecutar("/tmp/demo")
