"""Implementación de ejecución de procesos basada en subprocess."""

from __future__ import annotations

import subprocess

from aplicacion.puertos.ejecutor_procesos import EjecutorProcesos, ResultadoProceso


class EjecutorProcesosSubprocess(EjecutorProcesos):
    """Ejecuta comandos utilizando subprocess.run."""

    def ejecutar(self, comando: list[str], cwd: str) -> ResultadoProceso:
        completado = subprocess.run(
            comando,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return ResultadoProceso(
            codigo_salida=completado.returncode,
            stdout=completado.stdout,
            stderr=completado.stderr,
        )
