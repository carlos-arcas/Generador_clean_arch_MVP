"""Caso de uso para crear el plan base de un proyecto."""

from __future__ import annotations

from dominio.modelos import ArchivoGenerado, EspecificacionProyecto, PlanGeneracion


class CrearPlanProyectoBase:
    """Construye un plan de generación mínimo para iniciar un proyecto."""

    def ejecutar(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        """Crea un plan de archivos base a partir de la especificación."""
        especificacion.validar()

        descripcion = especificacion.descripcion or "Proyecto generado automáticamente."
        contenido_readme = (
            f"# {especificacion.nombre_proyecto}\n\n"
            f"{descripcion}\n\n"
            "## Inicio\n"
            "Este proyecto fue creado con generador_base_proyectos.\n"
        )
        contenido_changelog = (
            "# CHANGELOG\n\n"
            "## [No liberado]\n"
            f"- Inicialización de {especificacion.nombre_proyecto}.\n"
        )

        plan = PlanGeneracion(
            archivos=[
                ArchivoGenerado("README.md", contenido_readme),
                ArchivoGenerado("VERSION", especificacion.version),
                ArchivoGenerado("CHANGELOG.md", contenido_changelog),
                ArchivoGenerado("dominio/.gitkeep", ""),
                ArchivoGenerado("aplicacion/.gitkeep", ""),
                ArchivoGenerado("infraestructura/.gitkeep", ""),
                ArchivoGenerado("infraestructura/logging_config.py", _contenido_logging_config()),
                ArchivoGenerado("presentacion/.gitkeep", ""),
                ArchivoGenerado("tests/.gitkeep", ""),
                ArchivoGenerado("docs/.gitkeep", ""),
                ArchivoGenerado("logs/seguimiento.log", ""),
                ArchivoGenerado("logs/crashes.log", ""),
                ArchivoGenerado("scripts/lanzar_app.bat", "@echo off\npython -m presentacion\n"),
                ArchivoGenerado(
                    "scripts/ejecutar_tests.bat",
                    "@echo off\npytest --cov=. --cov-report=term-missing --cov-fail-under=85\n",
                ),
            ]
        )
        plan.comprobar_duplicados()
        return plan


def _contenido_logging_config() -> str:
    return (
        '"""Configuración de logging para seguimiento y crashes."""\n\n'
        "from __future__ import annotations\n\n"
        "import logging\n"
        "from pathlib import Path\n\n"
        "def configurar_logging(ruta_logs: str = \"logs\") -> None:\n"
        "    base = Path(ruta_logs)\n"
        "    base.mkdir(parents=True, exist_ok=True)\n"
        "    seguimiento = base / \"seguimiento.log\"\n"
        "    crashes = base / \"crashes.log\"\n"
        "    if not seguimiento.exists():\n"
        "        seguimiento.write_text(\"\", encoding=\"utf-8\")\n"
        "    if not crashes.exists():\n"
        "        crashes.write_text(\"\", encoding=\"utf-8\")\n\n"
        "    logging.basicConfig(\n"
        "        level=logging.INFO,\n"
        "        format=\"%(asctime)s | %(levelname)s | %(name)s | %(message)s\",\n"
        "        handlers=[\n"
        "            logging.FileHandler(seguimiento, encoding=\"utf-8\"),\n"
        "            logging.FileHandler(crashes, encoding=\"utf-8\"),\n"
        "        ],\n"
        "    )\n"
    )
