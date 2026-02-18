"""Caso de uso para construir una especificación de proyecto desde DTOs."""

from __future__ import annotations

from aplicacion.dtos.proyecto import DtoProyectoEntrada
from aplicacion.errores import ErrorValidacion
from dominio.modelos import ErrorValidacionDominio, EspecificacionAtributo, EspecificacionClase, EspecificacionProyecto


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
        if not dto.nombre_proyecto.strip():
            raise ErrorValidacion("El nombre del proyecto no puede estar vacío.")
        if not dto.ruta_destino.strip():
            raise ErrorValidacion("La ruta de destino no puede estar vacía.")

        for clase in dto.clases:
            if not clase.atributos:
                raise ErrorValidacion(
                    f"La clase '{clase.nombre.strip() or '(sin nombre)'}' debe tener al menos un atributo."
                )
            for atributo in clase.atributos:
                if atributo.tipo.strip() not in self.TIPOS_ATRIBUTO_VALIDOS:
                    raise ErrorValidacion(
                        f"El tipo '{atributo.tipo}' no es válido para el atributo '{atributo.nombre}'."
                    )
