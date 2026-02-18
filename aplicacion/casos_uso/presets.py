"""Casos de uso para persistir y recuperar presets."""

from __future__ import annotations

from dataclasses import asdict

from aplicacion.errores import ErrorValidacion
from aplicacion.puertos.almacen_presets import AlmacenPresets
from dominio.modelos import (
    EspecificacionAtributo,
    EspecificacionClase,
    EspecificacionProyecto,
    ErrorValidacionDominio,
    PresetProyecto,
)


def _crear_atributo_desde_payload(payload: dict) -> EspecificacionAtributo:
    kwargs = {
        "nombre": payload["nombre"],
        "tipo": payload["tipo"],
        "obligatorio": payload["obligatorio"],
        "valor_por_defecto": payload.get("valor_por_defecto"),
    }
    if payload.get("id_interno"):
        kwargs["id_interno"] = payload["id_interno"]
    return EspecificacionAtributo(**kwargs)


def _crear_clase_desde_payload(payload: dict) -> EspecificacionClase:
    kwargs = {
        "nombre": payload["nombre"],
        "atributos": [
            _crear_atributo_desde_payload(atributo) for atributo in payload.get("atributos", [])
        ],
    }
    if payload.get("id_interno"):
        kwargs["id_interno"] = payload["id_interno"]
    return EspecificacionClase(**kwargs)


class GuardarPreset:
    """Serializa y guarda un preset de configuración."""

    def __init__(self, almacen: AlmacenPresets) -> None:
        self._almacen = almacen

    def ejecutar(self, preset: PresetProyecto, incluir_ruta_destino: bool = False) -> str:
        try:
            preset.validar()
        except ErrorValidacionDominio as exc:
            raise ErrorValidacion(str(exc)) from exc

        payload = asdict(preset)
        if not incluir_ruta_destino:
            payload["especificacion"]["ruta_destino"] = ""
        return self._almacen.guardar(preset.nombre_preset, payload)


class CargarPreset:
    """Carga y valida un preset desde almacenamiento."""

    def __init__(self, almacen: AlmacenPresets) -> None:
        self._almacen = almacen

    def ejecutar(self, ruta: str, ruta_destino_forzada: str | None = None) -> PresetProyecto:
        try:
            payload = self._almacen.cargar(ruta)
            especificacion_payload = payload["especificacion"]
            especificacion = EspecificacionProyecto(
                nombre_proyecto=especificacion_payload["nombre_proyecto"],
                ruta_destino=(
                    ruta_destino_forzada
                    if ruta_destino_forzada is not None
                    else especificacion_payload.get("ruta_destino", "")
                ),
                descripcion=especificacion_payload.get("descripcion"),
                version=especificacion_payload.get("version", "0.1.0"),
                clases=[
                    _crear_clase_desde_payload(clase)
                    for clase in especificacion_payload.get("clases", [])
                ],
            )
            preset = PresetProyecto(
                nombre_preset=payload["nombre_preset"],
                especificacion=especificacion,
                blueprints=payload.get("blueprints", []),
                opciones=payload.get("opciones", {}),
            )
            preset.validar()
            return preset
        except KeyError as exc:
            raise ErrorValidacion(f"Preset inválido: falta la clave '{exc.args[0]}'.") from exc
        except (TypeError, ErrorValidacionDominio, ValueError) as exc:
            raise ErrorValidacion(f"Preset inválido: {exc}") from exc
