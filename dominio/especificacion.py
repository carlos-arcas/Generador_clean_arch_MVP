"""Modelos de dominio para definir la especificación de un proyecto."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from uuid import uuid4

from dominio.errores import ErrorValidacionDominio

PATRON_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
PATRON_PASCAL_CASE = re.compile(r"^[A-Z][A-Za-z0-9]*$")

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
