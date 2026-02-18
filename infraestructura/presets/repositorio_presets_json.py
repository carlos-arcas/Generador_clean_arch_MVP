"""Repositorio JSON para guardar, cargar y listar presets de proyecto."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile

from aplicacion.puertos.almacen_presets import AlmacenPresets
from dominio.especificacion import (
    ErrorValidacionDominio,
    EspecificacionAtributo,
    EspecificacionClase,
    EspecificacionProyecto,
)
from dominio.preset.preset_proyecto import PresetProyecto


class RepositorioPresetsJson(AlmacenPresets):
    """Persistencia de presets en `configuracion/presets/*.json`."""

    def __init__(self, directorio_presets: str = "configuracion/presets") -> None:
        self._directorio = Path(directorio_presets)

    def guardar(self, preset: PresetProyecto, ruta: str | None = None) -> str:
        self._directorio.mkdir(parents=True, exist_ok=True)
        ruta_destino = Path(ruta) if ruta else self._directorio / f"{preset.nombre}.json"
        payload = self._preset_a_dict(preset)

        descriptor, ruta_temporal = tempfile.mkstemp(
            dir=str(ruta_destino.parent),
            prefix=f".{ruta_destino.stem}.",
            suffix=".tmp",
        )
        ruta_temporal_path = Path(ruta_temporal)
        try:
            with open(descriptor, "w", encoding="utf-8", closefd=True) as archivo_temp:
                json.dump(payload, archivo_temp, ensure_ascii=False, indent=2)
            ruta_temporal_path.replace(ruta_destino)
        finally:
            if ruta_temporal_path.exists():
                ruta_temporal_path.unlink()
        return str(ruta_destino)

    def cargar(self, nombre_preset: str) -> PresetProyecto:
        ruta_preset = self._resolver_ruta_preset(nombre_preset)
        if not ruta_preset.exists():
            raise FileNotFoundError(f"No existe el preset: {nombre_preset}")

        try:
            payload = json.loads(ruta_preset.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON inválido en preset '{nombre_preset}': {exc.msg}") from exc
        return self._dict_a_preset(payload)

    def listar(self) -> list[str]:
        if not self._directorio.exists():
            return []
        return sorted(ruta.stem for ruta in self._directorio.glob("*.json"))

    def _resolver_ruta_preset(self, nombre_preset: str) -> Path:
        candidato = Path(nombre_preset)
        if candidato.suffix == ".json" or candidato.parent != Path("."):
            return candidato
        return self._directorio / f"{nombre_preset}.json"

    def _preset_a_dict(self, preset: PresetProyecto) -> dict:
        return {
            "nombre": preset.nombre,
            "especificacion": {
                "nombre_proyecto": preset.especificacion.nombre_proyecto,
                "descripcion": preset.especificacion.descripcion,
                "version": preset.especificacion.version,
                "ruta_destino": preset.especificacion.ruta_destino,
                "clases": [
                    {
                        "nombre": clase.nombre,
                        "atributos": [
                            {
                                "nombre": atributo.nombre,
                                "tipo": atributo.tipo,
                                "obligatorio": atributo.obligatorio,
                                "valor_por_defecto": atributo.valor_por_defecto,
                            }
                            for atributo in clase.atributos
                        ],
                    }
                    for clase in preset.especificacion.clases
                ],
            },
            "blueprints": preset.blueprints,
            "metadata": preset.metadata,
        }

    def _dict_a_preset(self, payload: dict) -> PresetProyecto:
        try:
            especificacion_payload = payload["especificacion"]
            preset = PresetProyecto(
                nombre=payload["nombre"],
                especificacion=EspecificacionProyecto(
                    nombre_proyecto=especificacion_payload.get("nombre_proyecto", ""),
                    ruta_destino=especificacion_payload.get("ruta_destino", "/tmp"),
                    descripcion=especificacion_payload.get("descripcion"),
                    version=especificacion_payload.get("version", "1.0.0"),
                    clases=[
                        EspecificacionClase(
                            nombre=clase_payload["nombre"],
                            atributos=[
                                EspecificacionAtributo(
                                    nombre=atributo_payload["nombre"],
                                    tipo=atributo_payload["tipo"],
                                    obligatorio=atributo_payload["obligatorio"],
                                    valor_por_defecto=atributo_payload.get("valor_por_defecto"),
                                )
                                for atributo_payload in clase_payload.get("atributos", [])
                            ],
                        )
                        for clase_payload in especificacion_payload.get("clases", [])
                    ],
                ),
                blueprints=payload.get("blueprints", []),
                metadata=payload.get("metadata", {}),
            )
            preset.validar()
            return preset
        except (KeyError, TypeError, ErrorValidacionDominio) as exc:
            raise ValueError(f"Estructura de preset inválida: {exc}") from exc
