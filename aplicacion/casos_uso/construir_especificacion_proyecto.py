"""Caso de uso para construir una especificación de proyecto desde DTOs."""

from __future__ import annotations

from aplicacion.dtos.proyecto import DtoProyectoEntrada
from aplicacion.errores import ErrorValidacion
from aplicacion.validacion import MotorValidacion, ReglaValidacion, ResultadoValidacion
from dominio.especificacion import (
    ErrorValidacionDominio,
    EspecificacionAtributo,
    EspecificacionClase,
    EspecificacionProyecto,
)


class _ReglaNombreProyecto(ReglaValidacion):
    def validar(self, contexto: DtoProyectoEntrada) -> ResultadoValidacion | None:
        if contexto.nombre_proyecto.strip():
            return None
        return ResultadoValidacion(False, "El nombre del proyecto no puede estar vacío.", "ERROR")


class _ReglaRutaDestino(ReglaValidacion):
    def validar(self, contexto: DtoProyectoEntrada) -> ResultadoValidacion | None:
        if contexto.ruta_destino.strip():
            return None
        return ResultadoValidacion(False, "La ruta de destino no puede estar vacía.", "ERROR")


class _ReglaClasesDuplicadas(ReglaValidacion):
    def validar(self, contexto: DtoProyectoEntrada) -> ResultadoValidacion | None:
        nombres = [clase.nombre.strip() for clase in contexto.clases]
        duplicadas = {nombre for nombre in nombres if nombre and nombres.count(nombre) > 1}
        if not duplicadas:
            return None
        mensaje = f"La especificación contiene clases duplicadas: {sorted(duplicadas)}"
        return ResultadoValidacion(False, mensaje, "ERROR")


class _ReglaAtributosValidos(ReglaValidacion):
    def validar(self, contexto: DtoProyectoEntrada) -> ResultadoValidacion | None:
        for clase in contexto.clases:
            if not clase.atributos:
                nombre = clase.nombre.strip() or "(sin nombre)"
                return ResultadoValidacion(False, f"La clase '{nombre}' debe tener al menos un atributo.", "ERROR")
            for atributo in clase.atributos:
                if not atributo.nombre.strip():
                    return ResultadoValidacion(False, "El nombre del atributo no puede estar vacío.", "ERROR")
        return None


class _ReglaTiposAtributo(ReglaValidacion):
    def __init__(self, tipos_validos: set[str]) -> None:
        self._tipos_validos = tipos_validos

    def validar(self, contexto: DtoProyectoEntrada) -> ResultadoValidacion | None:
        for clase in contexto.clases:
            for atributo in clase.atributos:
                if atributo.tipo.strip() not in self._tipos_validos:
                    mensaje = f"El tipo '{atributo.tipo}' no es válido para el atributo '{atributo.nombre}'."
                    return ResultadoValidacion(False, mensaje, "ERROR")
        return None


class ConstruirEspecificacionProyecto:
    """Valida DTOs de entrada y construye la entidad de dominio final."""

    TIPOS_ATRIBUTO_VALIDOS = {"str", "int", "float", "bool"}

    def __init__(self) -> None:
        self._motor_validacion = MotorValidacion(
            [
                _ReglaNombreProyecto(),
                _ReglaRutaDestino(),
                _ReglaClasesDuplicadas(),
                _ReglaAtributosValidos(),
                _ReglaTiposAtributo(self.TIPOS_ATRIBUTO_VALIDOS),
            ]
        )

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
        resultados = self._motor_validacion.ejecutar(dto)
        for resultado in resultados:
            if resultado.severidad == "ERROR" and not resultado.exito and resultado.mensaje:
                raise ErrorValidacion(resultado.mensaje)
