from infraestructura.ejecutor_procesos_subprocess import EjecutorProcesosSubprocess


def test_ejecutor_procesos_subprocess_ejecuta_comando() -> None:
    resultado = EjecutorProcesosSubprocess().ejecutar(["python", "-c", "print('ok')"], cwd=".")

    assert resultado.codigo_salida == 0
    assert "ok" in resultado.stdout
    assert resultado.stderr == ""
