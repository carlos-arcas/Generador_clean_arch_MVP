"""Pruebas unitarias del mapeo de errores a UX."""

from __future__ import annotations

from pathlib import Path

from presentacion.mapeo_mensajes_error import (
    MensajeUxError,
    construir_texto_para_copiar,
    mapear_error_a_mensaje_ux,
)


def test_mapear_error_permiso_da_mensaje_accionable() -> None:
    mensaje = mapear_error_a_mensaje_ux(
        PermissionError("sin permisos en carpeta"),
        id_incidente="GEN-20260101-101010-ABCD",
        ruta_logs=Path("logs"),
    )

    assert mensaje.acciones
    assert mensaje.causa_probable is not None
    assert "falló mvp" not in mensaje.mensaje.lower()


def test_mapear_error_inesperado_incluye_id_y_detalle_copiable() -> None:
    mensaje = mapear_error_a_mensaje_ux(
        RuntimeError("error no controlado"),
        id_incidente="GEN-20260101-101010-ABCD",
        ruta_logs=Path("logs"),
    )

    assert "GEN-20260101-101010-ABCD" in mensaje.mensaje
    assert mensaje.detalle_tecnico is not None


def test_construir_texto_para_copiar_incluye_id_y_ruta_logs() -> None:
    mensaje = MensajeUxError(
        titulo="Error inesperado",
        mensaje="Ocurrió un problema",
        causa_probable="Fallo interno",
        acciones=["Reintentar"],
        id_incidente="GEN-20260101-101010-ABCD",
        detalle_tecnico="traceback...",
        ruta_logs="logs",
    )

    texto = construir_texto_para_copiar(mensaje)

    assert "GEN-20260101-101010-ABCD" in texto
    assert "logs" in texto
    assert "traceback..." in texto
