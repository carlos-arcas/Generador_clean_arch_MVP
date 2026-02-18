"""Modelos de dominio para construir planes de generación."""

from __future__ import annotations

from dataclasses import dataclass, field

from dominio.especificacion import ErrorValidacionDominio


@dataclass(frozen=True)
class ArchivoGenerado:
    """Representa un archivo a crear dentro del plan de generación."""

    ruta_relativa: str
    contenido_texto: str


@dataclass
class PlanGeneracion:
    """Lista de archivos que serán generados para construir un proyecto base."""

    archivos: list[ArchivoGenerado] = field(default_factory=list)

    def agregar_archivo(self, archivo: ArchivoGenerado) -> None:
        """Agrega un archivo al plan actual."""
        self.archivos.append(archivo)

    def fusionar(self, otro_plan: PlanGeneracion) -> PlanGeneracion:
        """Fusiona este plan con otro y retorna un nuevo plan compuesto."""
        plan_fusionado = PlanGeneracion(archivos=[*self.archivos, *otro_plan.archivos])
        plan_fusionado.validar_sin_conflictos()
        return plan_fusionado

    def obtener_rutas(self) -> list[str]:
        """Retorna todas las rutas relativas incluidas en el plan."""
        return [archivo.ruta_relativa for archivo in self.archivos]

    def validar_sin_conflictos(self) -> None:
        """Valida que no existan rutas duplicadas en el plan."""
        rutas = self.obtener_rutas()
        rutas_duplicadas = {ruta for ruta in rutas if rutas.count(ruta) > 1}
        if rutas_duplicadas:
            raise ErrorValidacionDominio(
                f"El plan contiene rutas duplicadas: {sorted(rutas_duplicadas)}"
            )

    def comprobar_duplicados(self) -> None:
        """Compatibilidad retroactiva: delega a validar_sin_conflictos."""
        self.validar_sin_conflictos()
