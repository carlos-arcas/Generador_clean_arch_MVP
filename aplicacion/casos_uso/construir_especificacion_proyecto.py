"""Caso de uso para construir una especificación de proyecto desde DTOs."""

from __future__ import annotations

from aplicacion.dtos.proyecto import DtoAtributo, DtoProyectoEntrada
from aplicacion.errores import ErrorValidacion
from dominio.especificacion import (
    ErrorValidacionDominio,
    EspecificacionAtributo,
    EspecificacionClase,
    EspecificacionProyecto,
)


class ConstruirEspecificacionProyecto:
    """Valida DTOs de entrada y construye la entidad de dominio final."""

    TIPOS_ATRIBUTO_VALIDOS = {"str", "int", "float", "bool"}

    def ejecutar(self, dto: DtoProyectoEntrada) -> EspecificacionProyecto:
        self._validar_dto(dto)

        especificacion = EspecificacionProyecto(
            nombre_proyecto=dto.nombre_proyecto.strip(),
            ruta_destino=dto.ruta_destino.strip(),
            descripcion=dto.descripcion.strip(),
            version=dto.version.strip(),
        )

        try:
            for dto_clase in dto.clases:
                clase = EspecificacionClase(nombre=dto_clase.nombre.strip())
                for dto_atributo in dto_clase.atributos:
                    clase.agregar_atributo(
                        EspecificacionAtributo(
                            nombre=dto_atributo.nombre.strip(),
                            tipo=dto_atributo.tipo.strip(),
                            obligatorio=dto_atributo.obligatorio,
                        )
                    )
                especificacion.agregar_clase(clase)
            especificacion.validar()
        except ErrorValidacionDominio as exc:
            raise ErrorValidacion(str(exc)) from exc

        return especificacion

    def _validar_dto(self, dto: DtoProyectoEntrada) -> None:
        self._validar_nombre(dto)
        self._validar_ruta(dto)
        self._validar_clases(dto)
        self._validar_atributos(dto)
        self._validar_tipos(dto)

    def _validar_nombre(self, dto: DtoProyectoEntrada) -> None:
        if not dto.nombre_proyecto.strip():
            raise ErrorValidacion("El nombre del proyecto no puede estar vacío.")

    def _validar_ruta(self, dto: DtoProyectoEntrada) -> None:
        if not dto.ruta_destino.strip():
            raise ErrorValidacion("La ruta de destino no puede estar vacía.")

    def _validar_clases(self, dto: DtoProyectoEntrada) -> None:
        nombres = [clase.nombre.strip() for clase in dto.clases]
        duplicadas = {nombre for nombre in nombres if nombre and nombres.count(nombre) > 1}
        if duplicadas:
            raise ErrorValidacion(f"La especificación contiene clases duplicadas: {sorted(duplicadas)}")

    def _validar_atributos(self, dto: DtoProyectoEntrada) -> None:
        for clase in dto.clases:
            self._validar_atributos_por_clase(clase.nombre, clase.atributos)

    def _validar_atributos_por_clase(
        self,
        nombre_clase: str,
        atributos: list[DtoAtributo],
    ) -> None:
        if not atributos:
            nombre_clase_limpio = nombre_clase.strip() or "(sin nombre)"
            raise ErrorValidacion(
                f"La clase '{nombre_clase_limpio}' debe tener al menos un atributo."
            )
        for atributo in atributos:
            if not atributo.nombre.strip():
                raise ErrorValidacion("El nombre del atributo no puede estar vacío.")

    def _validar_tipos(self, dto: DtoProyectoEntrada) -> None:
        for clase in dto.clases:
            for atributo in clase.atributos:
                if atributo.tipo.strip() not in self.TIPOS_ATRIBUTO_VALIDOS:
                    raise ErrorValidacion(
                        f"El tipo '{atributo.tipo}' no es válido para el atributo '{atributo.nombre}'."
                    )
