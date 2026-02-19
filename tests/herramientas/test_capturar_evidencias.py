from __future__ import annotations

from pathlib import Path

from herramientas.capturar_evidencias import ResultadoEjecucion, capturar_evidencias_reproducibles


def _crear_estructura_repo(base: Path) -> None:
    (base / ".git").mkdir(parents=True, exist_ok=True)
    (base / "logs").mkdir(parents=True, exist_ok=True)


def test_construye_rutas_en_tmp_path_y_genera_documento(tmp_path: Path) -> None:
    _crear_estructura_repo(tmp_path)
    comandos: list[list[str]] = []

    def ejecutor_fake(comando: list[str], ruta_repo: Path) -> ResultadoEjecucion:
        assert ruta_repo == tmp_path
        comandos.append(comando)
        return ResultadoEjecucion(0, f"ok {' '.join(comando)}\n")

    codigo = capturar_evidencias_reproducibles(tmp_path, ejecutor=ejecutor_fake)

    assert codigo == 0
    assert (tmp_path / "docs" / "evidencias" / "auditor.txt").exists()
    assert (tmp_path / "docs" / "evidencias" / "pytest_q.txt").exists()
    assert (tmp_path / "docs" / "evidencias" / "coverage.txt").exists()
    assert (tmp_path / "docs" / "evidencias_reproducibles.md").exists()
    assert len(comandos) == 3


def test_escribe_ficheros_con_ejecutor_inyectado(tmp_path: Path) -> None:
    _crear_estructura_repo(tmp_path)

    respuestas = {
        "auditar_completitud_producto": ResultadoEjecucion(0, "auditor ok\n"),
        "-q": ResultadoEjecucion(0, "pytest ok\n"),
        "--cov=.": ResultadoEjecucion(0, "coverage ok\n"),
    }

    def ejecutor_fake(comando: list[str], _ruta_repo: Path) -> ResultadoEjecucion:
        clave = next((k for k in respuestas if any(k in parte for parte in comando)), "")
        return respuestas[clave]

    codigo = capturar_evidencias_reproducibles(tmp_path, ejecutor=ejecutor_fake)

    assert codigo == 0
    assert (tmp_path / "docs" / "evidencias" / "auditor.txt").read_text(encoding="utf-8") == "auditor ok\n"
    assert (tmp_path / "docs" / "evidencias" / "pytest_q.txt").read_text(encoding="utf-8") == "pytest ok\n"
    assert (tmp_path / "docs" / "evidencias" / "coverage.txt").read_text(encoding="utf-8") == "coverage ok\n"


def test_si_falla_comando_devuelve_error_y_deja_evidencia(tmp_path: Path) -> None:
    _crear_estructura_repo(tmp_path)

    def ejecutor_fake(comando: list[str], _ruta_repo: Path) -> ResultadoEjecucion:
        if any("auditar_completitud_producto" in parte for parte in comando):
            return ResultadoEjecucion(1, "auditor falló\n")
        return ResultadoEjecucion(0, "ok\n")

    codigo = capturar_evidencias_reproducibles(tmp_path, ejecutor=ejecutor_fake)

    assert codigo == 1
    assert (tmp_path / "docs" / "evidencias" / "auditor.txt").read_text(encoding="utf-8") == "auditor falló\n"
    assert not (tmp_path / "docs" / "evidencias_reproducibles.md").exists()
