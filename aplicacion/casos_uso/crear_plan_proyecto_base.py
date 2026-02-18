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
                ArchivoGenerado("logs/.gitkeep", ""),
                ArchivoGenerado("scripts/lanzar_app.bat", "@echo off\npython -m presentacion\n"),
                ArchivoGenerado(
                    "scripts/ejecutar_tests.bat",
                    "@echo off\npytest --cov=. --cov-report=term-missing --cov-fail-under=85\n",
                ),
            ]
        )
        plan.comprobar_duplicados()
        return plan
