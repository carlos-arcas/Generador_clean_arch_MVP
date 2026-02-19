from __future__ import annotations

from aplicacion.casos_uso.gestion_clases.modificar_clase import RenombrarClase
from aplicacion.casos_uso.gestion_clases.validaciones_clase import ListarClases
from aplicacion.dtos.proyecto.dto_atributo import DtoAtributo
from dominio.especificacion import EspecificacionClase, EspecificacionProyecto


class _RepositorioEspecificacionFake:
    def __init__(self, especificacion: EspecificacionProyecto) -> None:
        self._especificacion = especificacion
        self.guardados = 0

    def obtener(self) -> EspecificacionProyecto:
        return self._especificacion

    def guardar(self, especificacion: EspecificacionProyecto) -> None:
        self._especificacion = especificacion
        self.guardados += 1


def test_dto_atributo_expone_campos_publicos_esperados() -> None:
    dto = DtoAtributo(nombre="edad", tipo="int", obligatorio=True)

    assert dto.nombre == "edad"
    assert dto.tipo == "int"
    assert dto.obligatorio is True


def test_casos_uso_gestion_clases_lista_y_renombra() -> None:
    clase = EspecificacionClase(nombre="Cliente")
    repo = _RepositorioEspecificacionFake(
        EspecificacionProyecto(nombre_proyecto="Demo", ruta_destino="/tmp", clases=[clase])
    )

    clases = ListarClases(repo).ejecutar()
    actualizada = RenombrarClase(repo).ejecutar(clase.id_interno, "ClienteVip")

    assert len(clases) == 1
    assert actualizada.nombre == "ClienteVip"
    assert repo.guardados == 1
