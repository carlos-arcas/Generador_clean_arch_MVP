"""Paso para publicar manifest del proyecto generado."""

from __future__ import annotations

from aplicacion.casos_uso.generacion.pasos.errores_pipeline import ErrorPublicacionManifestGeneracion
from aplicacion.puertos.generador_manifest_puerto import GeneradorManifestPuerto
from dominio.especificacion import EspecificacionProyecto


class PublicadorManifestGeneracion:
    """Publica metadatos de generación si existe un generador de manifest."""

    def __init__(self, generador_manifest: GeneradorManifestPuerto | None) -> None:
        self._generador_manifest = generador_manifest

    def publicar(
        self,
        ruta_proyecto: str,
        especificacion_proyecto: EspecificacionProyecto,
        blueprints: list[str],
        archivos_generados: list[str],
    ) -> None:
        if self._generador_manifest is None:
            return
        try:
            self._generador_manifest.generar(
                ruta_proyecto=ruta_proyecto,
                especificacion_proyecto=especificacion_proyecto,
                blueprints=blueprints,
                archivos_generados=archivos_generados,
            )
        except (ValueError, OSError, RuntimeError) as exc:
            raise ErrorPublicacionManifestGeneracion(
                "No se pudo publicar el manifest del proyecto generado."
            ) from exc
