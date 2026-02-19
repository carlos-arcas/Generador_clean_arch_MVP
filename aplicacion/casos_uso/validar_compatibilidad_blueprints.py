"""Valida compatibilidad declarativa entre blueprints seleccionados."""

from __future__ import annotations

from aplicacion.dtos.blueprints import (
    DtoBlueprintMetadata,
    DtoConflictoBlueprint,
    DtoResultadoValidacionCompatibilidad,
)


class ValidarCompatibilidadBlueprints:
    def __init__(self, metadata_blueprints: dict[str, DtoBlueprintMetadata] | None = None) -> None:
        self._metadata = metadata_blueprints or {}

    def ejecutar(self, blueprints_seleccionados: list[str], hay_clases: bool) -> DtoResultadoValidacionCompatibilidad:
        conflictos: list[DtoConflictoBlueprint] = []
        warnings: list[str] = []

        metadatas = [self._metadata[nombre] for nombre in blueprints_seleccionados if nombre in self._metadata]
        desconocidos = sorted(set(blueprints_seleccionados) - set(self._metadata))
        if desconocidos:
            warnings.append(f"Sin metadata declarativa para: {', '.join(desconocidos)}")

        for indice, metadata_a in enumerate(metadatas):
            if metadata_a.requiere_clases and not hay_clases:
                conflictos.append(
                    DtoConflictoBlueprint(
                        codigo="VAL-DECL-001",
                        blueprint_a=metadata_a.nombre,
                        blueprint_b=None,
                        motivo="El blueprint requiere clases, pero no se definieron clases en el proyecto.",
                        accion_sugerida="Agrega al menos una clase o deselecciona el blueprint.",
                        regla_violada="requiere_clases",
                        tipo_blueprint_a=metadata_a.tipo,
                        entidad_a=metadata_a.entidad,
                    )
                )

            for metadata_b in metadatas[indice + 1 :]:
                if self._es_conflicto_mismo_tipo_entidad(metadata_a, metadata_b):
                    conflictos.append(
                        DtoConflictoBlueprint(
                            codigo="CON-DECL-001",
                            blueprint_a=metadata_a.nombre,
                            blueprint_b=metadata_b.nombre,
                            motivo="Dos blueprints CRUD_FULL para la misma entidad no son compatibles.",
                            accion_sugerida="Selecciona solo uno de los CRUD_FULL para la entidad.",
                            regla_violada="incompatible_con_mismo_tipo_y_entidad",
                            tipo_blueprint_a=metadata_a.tipo,
                            tipo_blueprint_b=metadata_b.tipo,
                            entidad_a=metadata_a.entidad,
                            entidad_b=metadata_b.entidad,
                        )
                    )
                    continue

                if self._es_conflicto_por_tipo(metadata_a, metadata_b):
                    conflictos.append(
                        DtoConflictoBlueprint(
                            codigo="CON-DECL-002",
                            blueprint_a=metadata_a.nombre,
                            blueprint_b=metadata_b.nombre,
                            motivo="La combinación de tipos de blueprint fue declarada como incompatible.",
                            accion_sugerida="Elimina uno de los blueprints incompatibles.",
                            regla_violada="incompatible_con_tipos",
                            tipo_blueprint_a=metadata_a.tipo,
                            tipo_blueprint_b=metadata_b.tipo,
                            entidad_a=metadata_a.entidad,
                            entidad_b=metadata_b.entidad,
                        )

                    )

        conflictos.extend(self._validar_compatible_con(metadatas))

        return DtoResultadoValidacionCompatibilidad(
            es_valido=not conflictos,
            conflictos=conflictos,
            warnings=warnings,
        )

    def _es_conflicto_mismo_tipo_entidad(self, metadata_a, metadata_b) -> bool:  # type: ignore[no-untyped-def]
        return (
            metadata_a.incompatible_con_mismo_tipo_y_entidad
            and metadata_b.incompatible_con_mismo_tipo_y_entidad
            and metadata_a.tipo == metadata_b.tipo == "CRUD_FULL"
            and metadata_a.entidad
            and metadata_a.entidad == metadata_b.entidad
        )

    def _es_conflicto_por_tipo(self, metadata_a, metadata_b) -> bool:  # type: ignore[no-untyped-def]
        return metadata_b.tipo in metadata_a.incompatible_con_tipos or metadata_a.tipo in metadata_b.incompatible_con_tipos

    def _validar_compatible_con(self, metadatas: list[object]) -> list[DtoConflictoBlueprint]:
        conflictos: list[DtoConflictoBlueprint] = []
        nombres = {getattr(metadata, "nombre", "") for metadata in metadatas}
        tipos = {getattr(metadata, "tipo", "") for metadata in metadatas}
        for metadata in metadatas:
            compatibilidades = set(getattr(metadata, "compatible_con", []))
            if not compatibilidades:
                continue
            if compatibilidades.intersection(nombres) or compatibilidades.intersection(tipos):
                continue
            conflictos.append(
                DtoConflictoBlueprint(
                    codigo="CON-DECL-002",
                    blueprint_a=getattr(metadata, "nombre", ""),
                    blueprint_b=None,
                    motivo="El blueprint requiere una compatibilidad explícita no satisfecha.",
                    accion_sugerida=f"Incluye alguno de: {sorted(compatibilidades)}.",
                    regla_violada="compatible_con",
                    tipo_blueprint_a=getattr(metadata, "tipo", None),
                    entidad_a=getattr(metadata, "entidad", None),
                )
            )
        return conflictos
