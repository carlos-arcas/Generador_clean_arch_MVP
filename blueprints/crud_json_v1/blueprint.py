"""Blueprint para generar CRUD + persistencia JSON siguiendo Clean Architecture."""

from __future__ import annotations

from dataclasses import dataclass
import textwrap

from aplicacion.puertos.blueprint import Blueprint
from dominio.especificacion import (
    EspecificacionClase,
    EspecificacionProyecto,
    ErrorValidacionDominio,
)
from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion


@dataclass(frozen=True)
class NombresClase:
    """Nombres derivados para plantillas de código generado."""

    nombre_clase: str
    nombre_snake: str
    nombre_plural: str


class CrudJsonBlueprint(Blueprint):
    """Genera estructura CRUD por entidad con repositorio JSON por archivo."""

    def nombre(self) -> str:
        return "crud_json"

    def version(self) -> str:
        return "1.0.0"

    def validar(self, especificacion: EspecificacionProyecto) -> None:
        especificacion.validar()
        if not especificacion.clases:
            raise ErrorValidacionDominio(
                "El blueprint crud_json requiere al menos una clase en la especificación."
            )

    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        self.validar(especificacion)

        archivos: list[ArchivoGenerado] = [ArchivoGenerado("datos/.gitkeep", "")]

        for clase in especificacion.clases:
            nombres = self._construir_nombres(clase)
            archivos.extend(
                [
                    ArchivoGenerado(
                        f"dominio/entidades/{nombres.nombre_snake}.py",
                        self._contenido_entidad(clase, nombres),
                    ),
                    ArchivoGenerado(
                        f"aplicacion/puertos/repositorio_{nombres.nombre_snake}.py",
                        self._contenido_puerto(nombres),
                    ),
                    ArchivoGenerado(
                        f"aplicacion/casos_uso/{nombres.nombre_snake}/crear_{nombres.nombre_snake}.py",
                        self._contenido_caso_uso_crear(clase, nombres),
                    ),
                    ArchivoGenerado(
                        f"aplicacion/casos_uso/{nombres.nombre_snake}/obtener_{nombres.nombre_snake}.py",
                        self._contenido_caso_uso_obtener(nombres),
                    ),
                    ArchivoGenerado(
                        f"aplicacion/casos_uso/{nombres.nombre_snake}/listar_{nombres.nombre_plural}.py",
                        self._contenido_caso_uso_listar(nombres),
                    ),
                    ArchivoGenerado(
                        f"aplicacion/casos_uso/{nombres.nombre_snake}/actualizar_{nombres.nombre_snake}.py",
                        self._contenido_caso_uso_actualizar(clase, nombres),
                    ),
                    ArchivoGenerado(
                        f"aplicacion/casos_uso/{nombres.nombre_snake}/eliminar_{nombres.nombre_snake}.py",
                        self._contenido_caso_uso_eliminar(nombres),
                    ),
                    ArchivoGenerado(
                        f"infraestructura/persistencia/json/repositorio_{nombres.nombre_snake}_json.py",
                        self._contenido_repositorio_json(nombres),
                    ),
                    ArchivoGenerado(
                        f"tests/aplicacion/test_crud_{nombres.nombre_snake}.py",
                        self._contenido_test_crud(clase, nombres),
                    ),
                    ArchivoGenerado(f"datos/{nombres.nombre_plural}.json", "[]\n"),
                ]
            )

        plan = PlanGeneracion(archivos=archivos)
        plan.validar_sin_conflictos()
        return plan

    def _construir_nombres(self, clase: EspecificacionClase) -> NombresClase:
        nombre_snake = self._pascal_a_snake(clase.nombre)
        return NombresClase(
            nombre_clase=clase.nombre,
            nombre_snake=nombre_snake,
            nombre_plural=self._pluralizar(nombre_snake),
        )

    def _pascal_a_snake(self, texto: str) -> str:
        caracteres: list[str] = []
        for indice, caracter in enumerate(texto):
            if caracter.isupper() and indice > 0:
                caracteres.append("_")
            caracteres.append(caracter.lower())
        return "".join(caracteres)

    def _pluralizar(self, nombre: str) -> str:
        if nombre.endswith(("a", "e", "i", "o", "u")):
            return f"{nombre}s"
        if nombre.endswith("s"):
            return nombre
        return f"{nombre}es"

    def _atributos_sin_id(self, clase: EspecificacionClase) -> list[str]:
        return [atributo.nombre for atributo in clase.atributos if atributo.nombre != "id"]

    def _tipo_python(self, tipo: str) -> str:
        normalizados = {
            "string": "str",
            "integer": "int",
            "float": "float",
            "bool": "bool",
        }
        return normalizados.get(tipo.lower(), tipo)

    def _contenido_entidad(self, clase: EspecificacionClase, nombres: NombresClase) -> str:
        campos = ["    id: int = 0"]
        validaciones: list[str] = []

        for atributo in clase.atributos:
            if atributo.nombre == "id":
                continue
            tipo = self._tipo_python(atributo.tipo)
            campos.append(f"    {atributo.nombre}: {tipo}")
            if tipo == "str":
                validaciones.append(
                    f"        if not self.{atributo.nombre}.strip():\n"
                    f"            raise ValueError(\"{atributo.nombre} no puede estar vacío.\")"
                )

        validaciones_texto = "\n".join(validaciones) or "        pass"
        return textwrap.dedent(
            f'''\
            """Entidad de dominio {nombres.nombre_clase}."""

            from __future__ import annotations

            from dataclasses import dataclass


            @dataclass
            class {nombres.nombre_clase}:
            {chr(10).join(campos)}

                def __post_init__(self) -> None:
                    if self.id < 0:
                        raise ValueError("id no puede ser negativo.")
            {validaciones_texto}
            '''
        )

    def _contenido_puerto(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            """Puerto de repositorio para {nombres.nombre_clase}."""

            from __future__ import annotations

            from abc import ABC, abstractmethod

            from dominio.entidades.{nombres.nombre_snake} import {nombres.nombre_clase}


            class Repositorio{nombres.nombre_clase}(ABC):
                @abstractmethod
                def crear(self, entidad: {nombres.nombre_clase}) -> {nombres.nombre_clase}:
                    """Crea una entidad y retorna la versión persistida."""

                @abstractmethod
                def obtener_por_id(self, entidad_id: int) -> {nombres.nombre_clase}:
                    """Obtiene una entidad por identificador."""

                @abstractmethod
                def listar(self) -> list[{nombres.nombre_clase}]:
                    """Lista todas las entidades."""

                @abstractmethod
                def actualizar(self, entidad: {nombres.nombre_clase}) -> {nombres.nombre_clase}:
                    """Actualiza una entidad existente."""

                @abstractmethod
                def eliminar(self, entidad_id: int) -> None:
                    """Elimina una entidad existente."""
            '''
        )

    def _firma_argumentos(self, clase: EspecificacionClase) -> str:
        partes: list[str] = []
        for atributo in clase.atributos:
            if atributo.nombre == "id":
                continue
            partes.append(f"{atributo.nombre}: {self._tipo_python(atributo.tipo)}")
        return ", ".join(partes)

    def _argumentos_ctor(self, clase: EspecificacionClase) -> str:
        partes = [
            f"{atributo.nombre}={atributo.nombre}"
            for atributo in clase.atributos
            if atributo.nombre != "id"
        ]
        return ", ".join(partes)

    def _contenido_caso_uso_crear(
        self, clase: EspecificacionClase, nombres: NombresClase
    ) -> str:
        firma = self._firma_argumentos(clase)
        ctor_args = self._argumentos_ctor(clase)
        return textwrap.dedent(
            f'''\
            """Caso de uso para crear {nombres.nombre_clase}."""

            from __future__ import annotations

            import logging

            from aplicacion.puertos.repositorio_{nombres.nombre_snake} import Repositorio{nombres.nombre_clase}
            from dominio.entidades.{nombres.nombre_snake} import {nombres.nombre_clase}

            LOGGER = logging.getLogger(__name__)


            class Crear{nombres.nombre_clase}:
                def __init__(self, repositorio: Repositorio{nombres.nombre_clase}) -> None:
                    self._repositorio = repositorio

                def ejecutar(self{', ' + firma if firma else ''}) -> {nombres.nombre_clase}:
                    LOGGER.info("Creando {nombres.nombre_clase}.")
                    entidad = {nombres.nombre_clase}(id=0{', ' + ctor_args if ctor_args else ''})
                    return self._repositorio.crear(entidad)
            '''
        )

    def _contenido_caso_uso_obtener(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            """Caso de uso para obtener {nombres.nombre_clase}."""

            from __future__ import annotations

            import logging

            from aplicacion.puertos.repositorio_{nombres.nombre_snake} import Repositorio{nombres.nombre_clase}
            from dominio.entidades.{nombres.nombre_snake} import {nombres.nombre_clase}

            LOGGER = logging.getLogger(__name__)


            class Obtener{nombres.nombre_clase}:
                def __init__(self, repositorio: Repositorio{nombres.nombre_clase}) -> None:
                    self._repositorio = repositorio

                def ejecutar(self, entidad_id: int) -> {nombres.nombre_clase}:
                    LOGGER.info("Obteniendo {nombres.nombre_clase} id=%s", entidad_id)
                    return self._repositorio.obtener_por_id(entidad_id)
            '''
        )

    def _contenido_caso_uso_listar(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            """Caso de uso para listar {nombres.nombre_plural}."""

            from __future__ import annotations

            import logging

            from aplicacion.puertos.repositorio_{nombres.nombre_snake} import Repositorio{nombres.nombre_clase}
            from dominio.entidades.{nombres.nombre_snake} import {nombres.nombre_clase}

            LOGGER = logging.getLogger(__name__)


            class Listar{nombres.nombre_clase}s:
                def __init__(self, repositorio: Repositorio{nombres.nombre_clase}) -> None:
                    self._repositorio = repositorio

                def ejecutar(self) -> list[{nombres.nombre_clase}]:
                    LOGGER.info("Listando {nombres.nombre_plural}.")
                    return self._repositorio.listar()
            '''
        )

    def _contenido_caso_uso_actualizar(
        self, clase: EspecificacionClase, nombres: NombresClase
    ) -> str:
        firma = self._firma_argumentos(clase)
        ctor_args = self._argumentos_ctor(clase)
        return textwrap.dedent(
            f'''\
            """Caso de uso para actualizar {nombres.nombre_clase}."""

            from __future__ import annotations

            import logging

            from aplicacion.puertos.repositorio_{nombres.nombre_snake} import Repositorio{nombres.nombre_clase}
            from dominio.entidades.{nombres.nombre_snake} import {nombres.nombre_clase}

            LOGGER = logging.getLogger(__name__)


            class Actualizar{nombres.nombre_clase}:
                def __init__(self, repositorio: Repositorio{nombres.nombre_clase}) -> None:
                    self._repositorio = repositorio

                def ejecutar(self, entidad_id: int{', ' + firma if firma else ''}) -> {nombres.nombre_clase}:
                    LOGGER.info("Actualizando {nombres.nombre_clase} id=%s", entidad_id)
                    entidad = {nombres.nombre_clase}(id=entidad_id{', ' + ctor_args if ctor_args else ''})
                    return self._repositorio.actualizar(entidad)
            '''
        )

    def _contenido_caso_uso_eliminar(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            """Caso de uso para eliminar {nombres.nombre_clase}."""

            from __future__ import annotations

            import logging

            from aplicacion.puertos.repositorio_{nombres.nombre_snake} import Repositorio{nombres.nombre_clase}

            LOGGER = logging.getLogger(__name__)


            class Eliminar{nombres.nombre_clase}:
                def __init__(self, repositorio: Repositorio{nombres.nombre_clase}) -> None:
                    self._repositorio = repositorio

                def ejecutar(self, entidad_id: int) -> None:
                    LOGGER.info("Eliminando {nombres.nombre_clase} id=%s", entidad_id)
                    self._repositorio.eliminar(entidad_id)
            '''
        )

    def _contenido_repositorio_json(self, nombres: NombresClase) -> str:
        partes = [
            self._generar_imports_repositorio_json(nombres),
            self._generar_definicion_clase_repositorio_json(nombres),
            self._generar_metodo_guardar_json(nombres),
            self._generar_metodo_obtener_json(nombres),
            self._generar_metodo_listar_json(nombres),
            self._generar_metodo_actualizar_json(nombres),
            self._generar_metodo_eliminar_json(nombres),
            self._generar_utilidades_json(),
        ]
        primera_parte = partes[0].rstrip("\n")
        resto = "\n\n".join(parte.strip("\n") for parte in partes[1:])
        return f"{primera_parte}\n\n\n{resto}\n"

    def _generar_imports_repositorio_json(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            """Implementación JSON del repositorio de {nombres.nombre_clase}."""

            from __future__ import annotations

            import json
            import logging
            from pathlib import Path
            import tempfile

            from aplicacion.puertos.repositorio_{nombres.nombre_snake} import Repositorio{nombres.nombre_clase}
            from dominio.entidades.{nombres.nombre_snake} import {nombres.nombre_clase}

            LOGGER = logging.getLogger(__name__)
            '''
        )

    def _generar_definicion_clase_repositorio_json(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            class Repositorio{nombres.nombre_clase}Json(Repositorio{nombres.nombre_clase}):
                def __init__(self, ruta_base: str) -> None:
                    self._ruta_archivo = Path(ruta_base) / "datos" / "{nombres.nombre_plural}.json"
                    self._ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
                    if not self._ruta_archivo.exists():
                        self._escribir_datos([])
            '''
        )

    def _generar_metodo_guardar_json(self, nombres: NombresClase) -> str:
        return self._indentar_bloque_clase(
            textwrap.dedent(
                f'''\
                def crear(self, entidad: {nombres.nombre_clase}) -> {nombres.nombre_clase}:
                    datos = self._leer_datos()
                    nuevo_id = max((item.get("id", 0) for item in datos), default=0) + 1
                    entidad_persistida = {nombres.nombre_clase}(**{{**entidad.__dict__, "id": nuevo_id}})
                    datos.append(entidad_persistida.__dict__)
                    self._escribir_datos(datos)
                    LOGGER.info("{nombres.nombre_clase} creada id=%s", nuevo_id)
                    return entidad_persistida
                '''
            )
        )

    def _generar_metodo_obtener_json(self, nombres: NombresClase) -> str:
        return self._indentar_bloque_clase(
            textwrap.dedent(
                f'''\
                def obtener_por_id(self, entidad_id: int) -> {nombres.nombre_clase}:
                    for item in self._leer_datos():
                        if item.get("id") == entidad_id:
                            return {nombres.nombre_clase}(**item)
                    raise ValueError("{nombres.nombre_clase} no encontrado")
                '''
            )
        )

    def _generar_metodo_listar_json(self, nombres: NombresClase) -> str:
        return self._indentar_bloque_clase(
            textwrap.dedent(
                f'''\
                def listar(self) -> list[{nombres.nombre_clase}]:
                    return [{nombres.nombre_clase}(**item) for item in self._leer_datos()]
                '''
            )
        )

    def _generar_metodo_actualizar_json(self, nombres: NombresClase) -> str:
        return self._indentar_bloque_clase(
            textwrap.dedent(
                f'''\
                def actualizar(self, entidad: {nombres.nombre_clase}) -> {nombres.nombre_clase}:
                    datos = self._leer_datos()
                    for indice, item in enumerate(datos):
                        if item.get("id") == entidad.id:
                            datos[indice] = entidad.__dict__
                            self._escribir_datos(datos)
                            LOGGER.info("{nombres.nombre_clase} actualizada id=%s", entidad.id)
                            return entidad
                    raise ValueError("{nombres.nombre_clase} no encontrado")
                '''
            )
        )

    def _generar_metodo_eliminar_json(self, nombres: NombresClase) -> str:
        return self._indentar_bloque_clase(
            textwrap.dedent(
                f'''\
                def eliminar(self, entidad_id: int) -> None:
                    datos = self._leer_datos()
                    filtrados = [item for item in datos if item.get("id") != entidad_id]
                    if len(filtrados) == len(datos):
                        raise ValueError("{nombres.nombre_clase} no encontrado")
                    self._escribir_datos(filtrados)
                    LOGGER.info("{nombres.nombre_clase} eliminada id=%s", entidad_id)
                '''
            )
        )

    def _generar_utilidades_json(self) -> str:
        bloque = "\n".join(
            [
                "def _leer_datos(self) -> list[dict]:",
                '    contenido = self._ruta_archivo.read_text(encoding="utf-8").strip()',
                "    if not contenido:",
                "        return []",
                "    return json.loads(contenido)",
                "",
                "def _escribir_datos(self, datos: list[dict]) -> None:",
                "    descriptor, ruta_tmp = tempfile.mkstemp(",
                "        dir=str(self._ruta_archivo.parent),",
                '        prefix=f".{self._ruta_archivo.name}.",',
                '        suffix=".tmp",',
                "    )",
                "    ruta_tmp_path = Path(ruta_tmp)",
                "    try:",
                '        with open(descriptor, "w", encoding="utf-8", closefd=True) as archivo_tmp:',
                "            json.dump(datos, archivo_tmp, ensure_ascii=False, indent=2)",
                '            archivo_tmp.write("\\n")',
                "        ruta_tmp_path.replace(self._ruta_archivo)",
                "    finally:",
                "        if ruta_tmp_path.exists():",
                "            ruta_tmp_path.unlink()",
            ]
        )
        return self._indentar_bloque_clase(bloque)

    def _indentar_bloque_clase(self, bloque: str) -> str:
        bloque_normalizado = textwrap.dedent(bloque).lstrip("\n").rstrip()
        return textwrap.indent(bloque_normalizado, "    ")

    def _contenido_test_crud(self, clase: EspecificacionClase, nombres: NombresClase) -> str:
        kwargs_crear = self._generar_kwargs_test(clase)
        kwargs_actualizar = self._generar_kwargs_test(clase, "_upd")
        assert_crear, assert_actualizar = self._generar_asserts_test(clase)

        partes = [
            self._generar_imports_test(nombres),
            self._generar_fixture_test(),
            self._generar_test_create(nombres, kwargs_crear, assert_crear),
            self._generar_test_read(nombres),
            self._generar_test_update(nombres, kwargs_crear, kwargs_actualizar, assert_actualizar),
            self._generar_test_delete(nombres, kwargs_crear),
            self._generar_utilidades_test(nombres),
        ]
        return "\n\n".join(parte for parte in partes if parte)

    def _valor_test(self, tipo_original: str, sufijo: str = "") -> str:
        tipo = self._tipo_python(tipo_original)
        if tipo == "str":
            return f'"valor{sufijo}"'
        if tipo == "int":
            return f"{10 if not sufijo else 20}"
        if tipo == "float":
            return f"{10.5 if not sufijo else 20.5}"
        if tipo == "bool":
            return "True" if not sufijo else "False"
        return f'"valor{sufijo}"'

    def _generar_kwargs_test(self, clase: EspecificacionClase, sufijo: str = "") -> str:
        return ", ".join(
            f"{atributo.nombre}={self._valor_test(atributo.tipo, sufijo)}"
            for atributo in clase.atributos
            if atributo.nombre != "id"
        )

    def _generar_asserts_test(self, clase: EspecificacionClase) -> tuple[str, str]:
        primer = next((a for a in clase.atributos if a.nombre != "id"), None)
        if primer is None:
            return "    assert creado.id == 1", "    assert actualizado.id == creado.id"

        tipo_primer = self._tipo_python(primer.tipo)
        if tipo_primer == "str":
            return f"    assert creado.{primer.nombre} == \"valor\"", f"    assert actualizado.{primer.nombre} == \"valor_upd\""
        if tipo_primer == "int":
            return f"    assert creado.{primer.nombre} == 10", f"    assert actualizado.{primer.nombre} == 20"
        if tipo_primer == "float":
            return f"    assert creado.{primer.nombre} == 10.5", f"    assert actualizado.{primer.nombre} == 20.5"
        return f"    assert creado.{primer.nombre} is True", f"    assert actualizado.{primer.nombre} is False"

    def _generar_imports_test(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            import pytest

            from dominio.entidades.{nombres.nombre_snake} import {nombres.nombre_clase}
            from infraestructura.persistencia.json.repositorio_{nombres.nombre_snake}_json import Repositorio{nombres.nombre_clase}Json
            '''
        )

    def _generar_fixture_test(self) -> str:
        return ""

    def _generar_test_create(self, nombres: NombresClase, kwargs_crear: str, assert_crear: str) -> str:
        return textwrap.dedent(
            f'''\
            def test_crear_ok(tmp_path) -> None:
                repo = Repositorio{nombres.nombre_clase}Json(str(tmp_path))

                creado = repo.crear({nombres.nombre_clase}(id=0{', ' + kwargs_crear if kwargs_crear else ''}))

                assert creado.id == 1
            {assert_crear}
            '''
        )

    def _generar_test_read(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            def test_obtener_inexistente_error(tmp_path) -> None:
                repo = Repositorio{nombres.nombre_clase}Json(str(tmp_path))

                with pytest.raises(ValueError, match="no encontrado"):
                    repo.obtener_por_id(404)
            '''
        )

    def _generar_test_update(
        self,
        nombres: NombresClase,
        kwargs_crear: str,
        kwargs_actualizar: str,
        assert_actualizar: str,
    ) -> str:
        return textwrap.dedent(
            f'''\
            def test_actualizar(tmp_path) -> None:
                repo = Repositorio{nombres.nombre_clase}Json(str(tmp_path))
                creado = repo.crear({nombres.nombre_clase}(id=0{', ' + kwargs_crear if kwargs_crear else ''}))

                actualizado = repo.actualizar(
                    {nombres.nombre_clase}(id=creado.id{', ' + kwargs_actualizar if kwargs_actualizar else ''})
                )

            {assert_actualizar}
            '''
        )

    def _generar_test_delete(self, nombres: NombresClase, kwargs_crear: str) -> str:
        return textwrap.dedent(
            f'''\
            def test_eliminar(tmp_path) -> None:
                repo = Repositorio{nombres.nombre_clase}Json(str(tmp_path))
                creado = repo.crear({nombres.nombre_clase}(id=0{', ' + kwargs_crear if kwargs_crear else ''}))

                repo.eliminar(creado.id)

                with pytest.raises(ValueError, match="no encontrado"):
                    repo.obtener_por_id(creado.id)
            '''
        )

    def _generar_utilidades_test(self, nombres: NombresClase) -> str:
        return textwrap.dedent(
            f'''\
            def test_listar_vacio_y_borde(tmp_path) -> None:
                repo = Repositorio{nombres.nombre_clase}Json(str(tmp_path))

                assert repo.listar() == []
            '''
        )
