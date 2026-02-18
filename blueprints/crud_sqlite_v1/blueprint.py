"""Blueprint para generar CRUD con persistencia SQLite intercambiable."""

from __future__ import annotations

import textwrap

from blueprints.crud_json_v1.blueprint import CrudJsonBlueprint, NombresClase
from dominio.especificacion import EspecificacionClase, EspecificacionProyecto
from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion


class CrudSqliteBlueprint(CrudJsonBlueprint):
    """Genera CRUD por entidad reutilizando dominio/aplicación y cambiando persistencia a SQLite."""

    def nombre(self) -> str:
        return "crud_sqlite"

    def version(self) -> str:
        return "1.0.0"

    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        self.validar(especificacion)
        archivos: list[ArchivoGenerado] = [ArchivoGenerado("datos/.gitkeep", "")]

        for clase in especificacion.clases:
            nombres = self._construir_nombres(clase)
            archivos.extend(
                [
                    ArchivoGenerado(f"dominio/entidades/{nombres.nombre_snake}.py", self._contenido_entidad(clase, nombres)),
                    ArchivoGenerado(
                        f"aplicacion/puertos/repositorio_{nombres.nombre_snake}.py", self._contenido_puerto(nombres)
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
                        f"infraestructura/persistencia/sqlite/repositorio_{nombres.nombre_snake}_sqlite.py",
                        self._contenido_repositorio_sqlite(clase, nombres),
                    ),
                    ArchivoGenerado(
                        f"tests/aplicacion/test_crud_{nombres.nombre_snake}.py",
                        self._contenido_test_crud_sqlite(clase, nombres),
                    ),
                ]
            )

        plan = PlanGeneracion(archivos=archivos)
        plan.validar_sin_conflictos()
        return plan

    def _tipo_sqlite(self, tipo: str) -> str:
        normalizados = {
            "str": "TEXT",
            "string": "TEXT",
            "int": "INTEGER",
            "integer": "INTEGER",
            "float": "REAL",
            "bool": "INTEGER",
            "boolean": "INTEGER",
        }
        return normalizados.get(tipo.lower(), "TEXT")

    def _contenido_repositorio_sqlite(self, clase: EspecificacionClase, nombres: NombresClase) -> str:
        atributos_sin_id = [atributo for atributo in clase.atributos if atributo.nombre != "id"]
        columnas_sql = ["id INTEGER PRIMARY KEY AUTOINCREMENT"] + [
            f"{atributo.nombre} {self._tipo_sqlite(atributo.tipo)}" for atributo in atributos_sin_id
        ]
        columnas_sql_texto = ",\n                ".join(columnas_sql)

        if atributos_sin_id:
            nombres_columnas = ", ".join(atributo.nombre for atributo in atributos_sin_id)
            placeholders = ", ".join("?" for _ in atributos_sin_id)
            insert_sql = f'"INSERT INTO {nombres.nombre_plural} ({nombres_columnas}) VALUES ({placeholders})"'
            params_crear = f"({', '.join(f'entidad.{atributo.nombre}' for atributo in atributos_sin_id)},)"
            set_clause = ", ".join(f"{atributo.nombre} = ?" for atributo in atributos_sin_id)
            params_actualizar = (
                f"({', '.join(f'entidad.{atributo.nombre}' for atributo in atributos_sin_id)}, entidad.id)"
            )
            retorno_crear = ", ".join(f"{atributo.nombre}=entidad.{atributo.nombre}" for atributo in atributos_sin_id)
            retorno_crear = f", {retorno_crear}" if retorno_crear else ""
        else:
            insert_sql = f'"INSERT INTO {nombres.nombre_plural} DEFAULT VALUES"'
            params_crear = "()"
            set_clause = "id = id"
            params_actualizar = "(entidad.id,)"
            retorno_crear = ""

        conversiones = []
        for atributo in atributos_sin_id:
            tipo = self._tipo_python(atributo.tipo)
            if tipo == "bool":
                conversiones.append(f"            {atributo.nombre}=bool(fila['{atributo.nombre}']),")
            else:
                conversiones.append(f"            {atributo.nombre}=fila['{atributo.nombre}'],")
        conversiones_texto = "\n".join(conversiones)

        return textwrap.dedent(
            f'''\
            """Implementación SQLite del repositorio de {nombres.nombre_clase}."""

            from __future__ import annotations

            import logging
            from pathlib import Path
            import sqlite3

            from aplicacion.puertos.repositorio_{nombres.nombre_snake} import Repositorio{nombres.nombre_clase}
            from dominio.entidades.{nombres.nombre_snake} import {nombres.nombre_clase}

            LOGGER = logging.getLogger(__name__)


            class Repositorio{nombres.nombre_clase}Sqlite(Repositorio{nombres.nombre_clase}):
                def __init__(self, ruta_base: str) -> None:
                    self._ruta_db = Path(ruta_base) / "datos" / "base_datos.db"
                    self._ruta_db.parent.mkdir(parents=True, exist_ok=True)
                    self._asegurar_tabla()

                def crear(self, entidad: {nombres.nombre_clase}) -> {nombres.nombre_clase}:
                    try:
                        with self._conectar() as conexion:
                            cursor = conexion.execute({insert_sql}, {params_crear})
                            persistida = {nombres.nombre_clase}(id=int(cursor.lastrowid){retorno_crear})
                            LOGGER.info("{nombres.nombre_clase} creada id=%s", persistida.id)
                            return persistida
                    except sqlite3.Error as exc:
                        LOGGER.exception("Error SQL al crear {nombres.nombre_clase}")
                        raise ValueError("Error SQL al crear entidad") from exc

                def obtener_por_id(self, entidad_id: int) -> {nombres.nombre_clase}:
                    try:
                        with self._conectar() as conexion:
                            fila = conexion.execute(
                                "SELECT * FROM {nombres.nombre_plural} WHERE id = ?",
                                (entidad_id,),
                            ).fetchone()
                            if fila is None:
                                raise ValueError("{nombres.nombre_clase} no encontrado")
                            return self._fila_a_entidad(fila)
                    except sqlite3.Error as exc:
                        LOGGER.exception("Error SQL al obtener {nombres.nombre_clase} id=%s", entidad_id)
                        raise ValueError("Error SQL al obtener entidad") from exc

                def listar(self) -> list[{nombres.nombre_clase}]:
                    try:
                        with self._conectar() as conexion:
                            filas = conexion.execute(
                                "SELECT * FROM {nombres.nombre_plural} ORDER BY id ASC"
                            ).fetchall()
                            entidades = [self._fila_a_entidad(fila) for fila in filas]
                            LOGGER.info("Listado de {nombres.nombre_clase}: %s elementos", len(entidades))
                            return entidades
                    except sqlite3.Error as exc:
                        LOGGER.exception("Error SQL al listar {nombres.nombre_clase}")
                        raise ValueError("Error SQL al listar entidades") from exc

                def actualizar(self, entidad: {nombres.nombre_clase}) -> {nombres.nombre_clase}:
                    try:
                        with self._conectar() as conexion:
                            cursor = conexion.execute(
                                "UPDATE {nombres.nombre_plural} SET {set_clause} WHERE id = ?",
                                {params_actualizar},
                            )
                            if cursor.rowcount == 0:
                                raise ValueError("{nombres.nombre_clase} no encontrado")
                            LOGGER.info("{nombres.nombre_clase} actualizada id=%s", entidad.id)
                            return entidad
                    except sqlite3.Error as exc:
                        LOGGER.exception("Error SQL al actualizar {nombres.nombre_clase} id=%s", entidad.id)
                        raise ValueError("Error SQL al actualizar entidad") from exc

                def eliminar(self, entidad_id: int) -> None:
                    try:
                        with self._conectar() as conexion:
                            cursor = conexion.execute(
                                "DELETE FROM {nombres.nombre_plural} WHERE id = ?",
                                (entidad_id,),
                            )
                            if cursor.rowcount == 0:
                                raise ValueError("{nombres.nombre_clase} no encontrado")
                            LOGGER.info("{nombres.nombre_clase} eliminada id=%s", entidad_id)
                    except sqlite3.Error as exc:
                        LOGGER.exception("Error SQL al eliminar {nombres.nombre_clase} id=%s", entidad_id)
                        raise ValueError("Error SQL al eliminar entidad") from exc

                def _asegurar_tabla(self) -> None:
                    LOGGER.info("Creando tabla {nombres.nombre_plural} si no existe")
                    with self._conectar() as conexion:
                        conexion.execute(
                            """
                            CREATE TABLE IF NOT EXISTS {nombres.nombre_plural} (
                                {columnas_sql_texto}
                            )
                            """
                        )

                def _conectar(self) -> sqlite3.Connection:
                    conexion = sqlite3.connect(self._ruta_db)
                    conexion.row_factory = sqlite3.Row
                    return conexion

                def _fila_a_entidad(self, fila: sqlite3.Row) -> {nombres.nombre_clase}:
                    return {nombres.nombre_clase}(
                        id=int(fila["id"]),
            {conversiones_texto}
                    )
            '''
        )

    def _contenido_test_crud_sqlite(self, clase: EspecificacionClase, nombres: NombresClase) -> str:
        contenido_json = self._contenido_test_crud(clase, nombres)
        return contenido_json.replace(
            f"from infraestructura.persistencia.json.repositorio_{nombres.nombre_snake}_json import Repositorio{nombres.nombre_clase}Json",
            f"from infraestructura.persistencia.sqlite.repositorio_{nombres.nombre_snake}_sqlite import Repositorio{nombres.nombre_clase}Sqlite",
        ).replace(f"Repositorio{nombres.nombre_clase}Json", f"Repositorio{nombres.nombre_clase}Sqlite")
