from pathlib import Path
import shutil

from presentacion.__main__ import main


def test_main_ejecuta_flujo_minimo_generando_archivos() -> None:
    destino = Path("salida") / "proyecto_demo"
    if destino.exists():
        shutil.rmtree(destino)

    main()

    assert (destino / "README.md").exists()
    assert (destino / "VERSION").exists()
    assert (destino / "CHANGELOG.md").exists()
