"""Modelos de dominio para especificación y planificación de generación."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, List
from uuid import uuid4

PATRON_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
PATRON_PASCAL_CASE = re.compile(r"^[A-Z][A-Za-z0-9]*$")


class ErrorValidacionDominio(ValueError):
    """Error de validación para entidades de dominio."""


@dataclass
class EspecificacionAtributo:
    """Representa un atributo de una clase en el constructor dinámico.

    Nota de coherencia: cuando ``obligatorio=True`` y ``valor_por_defecto=None``
    el estado es válido; indica que el atributo deberá proporcionarse explícitamente.
    """

    nombre: str
    tipo: str
    obligatorio: bool
    valor_por_defecto: str | None = None
    id_interno: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.id_interno.strip():
            raise ErrorValidacionDominio("El id_interno del atributo es obligatorio.")
        if not self.nombre or not self.nombre.strip():
            raise ErrorValidacionDominio("El nombre del atributo no puede estar vacío.")
        if " " in self.nombre:
            raise ErrorValidacionDominio("El nombre del atributo no puede contener espacios.")
        if not self.tipo or not self.tipo.strip():
            raise ErrorValidacionDominio("El tipo del atributo no puede estar vacío.")


@dataclass
class EspecificacionClase:
    """Representa una clase del dominio que será generada dinámicamente."""

    nombre: str
    atributos: list[EspecificacionAtributo] = field(default_factory=list)
    id_interno: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.id_interno.strip():
            raise ErrorValidacionDominio("El id_interno de la clase es obligatorio.")
        if not self.nombre or not self.nombre.strip():
            raise ErrorValidacionDominio("El nombre de la clase no puede estar vacío.")
        if " " in self.nombre:
            raise ErrorValidacionDominio("El nombre de la clase no puede contener espacios.")
        if not PATRON_PASCAL_CASE.match(self.nombre):
            raise ErrorValidacionDominio("El nombre de la clase debe estar en formato PascalCase.")
        self._validar_atributos_duplicados()

    def _validar_atributos_duplicados(self) -> None:
        nombres = [atributo.nombre for atributo in self.atributos]
        duplicados = {nombre for nombre in nombres if nombres.count(nombre) > 1}
        if duplicados:
            raise ErrorValidacionDominio(
                f"La clase contiene atributos duplicados: {sorted(duplicados)}"
            )

    def agregar_atributo(self, atributo: EspecificacionAtributo) -> None:
        if any(item.nombre == atributo.nombre for item in self.atributos):
            raise ErrorValidacionDominio(
                f"Ya existe un atributo con nombre '{atributo.nombre}'."
            )
        self.atributos.append(atributo)

    def obtener_atributo(self, id_interno: str) -> EspecificacionAtributo:
        for atributo in self.atributos:
            if atributo.id_interno == id_interno:
                return atributo
        raise ErrorValidacionDominio(
            f"No existe un atributo con id_interno '{id_interno}'."
        )

    def eliminar_atributo(self, id_interno: str) -> None:
        atributo = self.obtener_atributo(id_interno)
        self.atributos.remove(atributo)

    def editar_atributo(
        self,
        id_interno: str,
        nombre: str,
        tipo: str,
        obligatorio: bool,
        valor_por_defecto: str | None,
    ) -> EspecificacionAtributo:
        atributo_original = self.obtener_atributo(id_interno)
        candidato = EspecificacionAtributo(
            id_interno=id_interno,
            nombre=nombre,
            tipo=tipo,
            obligatorio=obligatorio,
            valor_por_defecto=valor_por_defecto,
        )
        if any(
            item.nombre == candidato.nombre and item.id_interno != id_interno
            for item in self.atributos
        ):
            raise ErrorValidacionDominio(
                f"Ya existe un atributo con nombre '{candidato.nombre}'."
            )
        indice = self.atributos.index(atributo_original)
        self.atributos[indice] = candidato
        return candidato


@dataclass
class EspecificacionProyecto:
    """Define los datos mínimos requeridos para generar un proyecto base."""

    nombre_proyecto: str
    ruta_destino: str
    descripcion: str | None = None
    version: str = "0.1.0"
    clases: list[EspecificacionClase] = field(default_factory=list)

    def validar(self) -> None:
        """Valida la especificación del proyecto y falla si hay datos inválidos."""
        if not self.nombre_proyecto or not self.nombre_proyecto.strip():
            raise ErrorValidacionDominio("El nombre del proyecto no puede estar vacío.")

        if not self.ruta_destino or not self.ruta_destino.strip():
            raise ErrorValidacionDominio("La ruta de destino no puede estar vacía.")

        if not PATRON_SEMVER.match(self.version):
            raise ErrorValidacionDominio("La versión debe cumplir el formato X.Y.Z.")

        nombres = [clase.nombre for clase in self.clases]
        duplicadas = {nombre for nombre in nombres if nombres.count(nombre) > 1}
        if duplicadas:
            raise ErrorValidacionDominio(
                f"La especificación contiene clases duplicadas: {sorted(duplicadas)}"
            )

    def agregar_clase(self, clase: EspecificacionClase) -> None:
        if any(item.nombre == clase.nombre for item in self.clases):
            raise ErrorValidacionDominio(f"Ya existe una clase con nombre '{clase.nombre}'.")
        self.clases.append(clase)

    def obtener_clase(self, id_interno: str) -> EspecificacionClase:
        for clase in self.clases:
            if clase.id_interno == id_interno:
                return clase
        raise ErrorValidacionDominio(f"No existe una clase con id_interno '{id_interno}'.")

    def eliminar_clase(self, id_interno: str) -> None:
        clase = self.obtener_clase(id_interno)
        self.clases.remove(clase)

    def renombrar_clase(self, id_interno: str, nuevo_nombre: str) -> EspecificacionClase:
        clase = self.obtener_clase(id_interno)
        candidato = EspecificacionClase(
            id_interno=clase.id_interno,
            nombre=nuevo_nombre,
            atributos=clase.atributos.copy(),
        )
        if any(
            item.nombre == candidato.nombre and item.id_interno != id_interno
            for item in self.clases
        ):
            raise ErrorValidacionDominio(
                f"Ya existe una clase con nombre '{candidato.nombre}'."
            )
        indice = self.clases.index(clase)
        self.clases[indice] = candidato
        return candidato

    def listar_clases(self) -> list[EspecificacionClase]:
        return self.clases.copy()




@dataclass
class PresetProyecto:
    """Configuración reusable para generación de proyecto."""

    nombre_preset: str
    especificacion: EspecificacionProyecto
    blueprints: list[str]
    opciones: dict[str, Any] = field(default_factory=dict)

    def validar(self) -> None:
        if not self.nombre_preset or not self.nombre_preset.strip():
            raise ErrorValidacionDominio("El nombre del preset no puede estar vacío.")
        self.especificacion.validar()
        if not self.blueprints:
            raise ErrorValidacionDominio("El preset debe incluir al menos un blueprint.")

@dataclass(frozen=True)
class ArchivoGenerado:
    """Representa un archivo a crear dentro del plan de generación."""

    ruta_relativa: str
    contenido_texto: str


@dataclass
class PlanGeneracion:
    """Lista de archivos que serán generados para construir un proyecto base."""

    archivos: List[ArchivoGenerado] = field(default_factory=list)

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


@dataclass(frozen=True)
class EntradaManifest:
    """Representa una entrada de archivo en el manifest generado."""

    ruta_relativa: str
    hash_sha256: str

    def __post_init__(self) -> None:
        if not self.ruta_relativa.strip():
            raise ErrorValidacionDominio("La ruta del manifest no puede estar vacía.")
        if not self.hash_sha256.strip():
            raise ErrorValidacionDominio("El hash SHA256 es obligatorio en el manifest.")


@dataclass
class ManifestProyecto:
    """Representa la metadata de generación del proyecto."""

    version_generador: str
    blueprints_usados: list[str]
    archivos: list[EntradaManifest]
    timestamp_generacion: str
    opciones: dict[str, Any]

    def __post_init__(self) -> None:
        rutas = [entrada.ruta_relativa for entrada in self.archivos]
        duplicadas = {ruta for ruta in rutas if rutas.count(ruta) > 1}
        if duplicadas:
            raise ErrorValidacionDominio(
                f"El manifest contiene rutas duplicadas: {sorted(duplicadas)}"
            )

    def obtener_clases_generadas(self) -> list[str]:
        """Infiera clases generadas recorriendo rutas de entidades en manifest."""
        clases: set[str] = set()
        for entrada in self.archivos:
            if not entrada.ruta_relativa.startswith("dominio/entidades/"):
                continue
            if not entrada.ruta_relativa.endswith(".py"):
                continue
            nombre_archivo = entrada.ruta_relativa.rsplit("/", maxsplit=1)[-1].removesuffix(".py")
            clases.add("".join(segmento.capitalize() for segmento in nombre_archivo.split("_")))
        return sorted(clases)
