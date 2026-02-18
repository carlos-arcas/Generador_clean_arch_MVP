from pathlib import Path

from aplicacion.casos_uso.ejecutar_plan import EjecutarPlan
from dominio.modelos import ArchivoGenerado, PlanGeneracion
from infraestructura.sistema_archivos_real import SistemaArchivosReal


class SistemaArchivosDoble:
    def __init__(self) -> None:
        self.directorios: list[str] = []
        self.escrituras: list[tuple[str, str]] = []

    def escribir_texto_atomico(self, ruta_absoluta: str, contenido: str) -> None:
        self.escrituras.append((ruta_absoluta, contenido))

    def asegurar_directorio(self, ruta_absoluta: str) -> None:
        self.directorios.append(ruta_absoluta)


def test_ejecutar_plan_invoca_puerto_para_todos_los_archivos(tmp_path: Path) -> None:
    plan = PlanGeneracion(
        archivos=[
            ArchivoGenerado("README.md", "contenido"),
            ArchivoGenerado("sub/VERSION", "1.0.0"),
        ]
    )
    doble = SistemaArchivosDoble()

    EjecutarPlan(doble).ejecutar(plan, str(tmp_path))

    assert len(doble.directorios) == 2
    assert len(doble.escrituras) == 2


def test_sistema_archivos_real_escribe_archivo_atomico(tmp_path: Path) -> None:
    sistema = SistemaArchivosReal()
    ruta = tmp_path / "demo" / "archivo.txt"

    sistema.escribir_texto_atomico(str(ruta), "hola")

    assert ruta.exists()
    assert ruta.read_text(encoding="utf-8") == "hola"


class GeneradorManifestDoble:
    def __init__(self) -> None:
        self.llamadas: list[dict[str, object]] = []

    def ejecutar(self, **kwargs: object) -> None:
        self.llamadas.append(kwargs)


def test_ejecutar_plan_dispara_generacion_manifest(tmp_path: Path) -> None:
    plan = PlanGeneracion(archivos=[ArchivoGenerado("README.md", "contenido")])
    doble_fs = SistemaArchivosDoble()
    doble_manifest = GeneradorManifestDoble()

    EjecutarPlan(doble_fs, doble_manifest).ejecutar(
        plan,
        str(tmp_path),
        opciones={"modo": "prueba"},
        version_generador="0.2.0",
        blueprints_usados=["base_clean_arch@1.0.0"],
    )

    assert len(doble_manifest.llamadas) == 1
