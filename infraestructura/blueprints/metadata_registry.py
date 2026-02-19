"""Registro de metadata declarativa para blueprints internos y plugins conocidos."""

from __future__ import annotations

from aplicacion.dtos.blueprints import DtoBlueprintMetadata


def obtener_metadata_blueprints() -> dict[str, DtoBlueprintMetadata]:
    return {
        "base_clean_arch": DtoBlueprintMetadata(
            nombre="base_clean_arch",
            descripcion="Estructura base Clean Architecture.",
            tipo="CRUD_BASE",
            entidad=None,
            requiere_clases=False,
            genera_capas=["dominio", "aplicacion", "infraestructura", "tests"],
        ),
        "crud_json": DtoBlueprintMetadata(
            nombre="crud_json",
            descripcion="CRUD completo con persistencia JSON.",
            tipo="CRUD_FULL",
            entidad="persona",
            requiere_clases=True,
            genera_capas=["dominio", "aplicacion", "infraestructura", "tests"],
            incompatible_con_tipos=["CRUD_FULL"],
            incompatible_con_mismo_tipo_y_entidad=True,
        ),
        "crud_sqlite": DtoBlueprintMetadata(
            nombre="crud_sqlite",
            descripcion="CRUD completo con persistencia SQLite.",
            tipo="CRUD_FULL",
            entidad="persona",
            requiere_clases=True,
            genera_capas=["dominio", "aplicacion", "infraestructura", "tests"],
            incompatible_con_tipos=["CRUD_FULL"],
            incompatible_con_mismo_tipo_y_entidad=True,
        ),
        "export_csv": DtoBlueprintMetadata(
            nombre="export_csv",
            descripcion="Exportación de datos en CSV.",
            tipo="EXPORT",
            entidad=None,
            requiere_clases=False,
            genera_capas=["infraestructura", "tests"],
        ),
        "export_excel": DtoBlueprintMetadata(
            nombre="export_excel",
            descripcion="Exportación de datos en Excel.",
            tipo="EXPORT",
            entidad=None,
            requiere_clases=False,
            genera_capas=["infraestructura", "tests"],
        ),
        "export_pdf": DtoBlueprintMetadata(
            nombre="export_pdf",
            descripcion="Exportación de datos en PDF.",
            tipo="EXPORT",
            entidad=None,
            requiere_clases=False,
            genera_capas=["infraestructura", "tests"],
        ),
        "api_fastapi": DtoBlueprintMetadata(
            nombre="api_fastapi",
            descripcion="API de exposición FastAPI para el dominio generado.",
            tipo="API",
            entidad=None,
            requiere_clases=False,
            genera_capas=["presentacion", "tests"],
            compatible_con=["CRUD_FULL"],
        ),
    }
