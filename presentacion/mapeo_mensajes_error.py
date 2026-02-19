"""Mapeo centralizado de errores técnicos a mensajes UX accionables."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import traceback

from aplicacion.errores import ErrorValidacionEntrada


@dataclass(frozen=True)
class MensajeUxError:
    """Contrato de mensaje de error para la interfaz de usuario."""

    titulo: str
    mensaje: str
    causa_probable: str | None
    acciones: list[str]
    id_incidente: str
    detalle_tecnico: str | None
    ruta_logs: str | None


def _construir_detalle_tecnico(exc: Exception, id_incidente: str) -> str:
    detalle_traceback = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return f"id_incidente={id_incidente}\nerror={exc!r}\n\n{detalle_traceback}".strip()


def mapear_error_a_mensaje_ux(
    exc: Exception,
    id_incidente: str,
    ruta_logs: Path | None,
) -> MensajeUxError:
    """Mapea errores a un mensaje amigable y accionable para el usuario final."""
    ruta_logs_texto = str(ruta_logs) if ruta_logs else None

    if isinstance(exc, (ErrorValidacionEntrada, ValueError, TypeError, FileExistsError)):
        return MensajeUxError(
            titulo="No se pudo iniciar la generación",
            mensaje="Revisa los datos ingresados y corrige los campos marcados.",
            causa_probable=str(exc) or "Se detectó una entrada inválida.",
            acciones=[
                "Corrige el nombre/ruta del proyecto.",
                "Verifica que el proyecto no exista previamente.",
                "Vuelve a intentar la generación.",
            ],
            id_incidente=id_incidente,
            detalle_tecnico=_construir_detalle_tecnico(exc, id_incidente),
            ruta_logs=ruta_logs_texto,
        )

    if isinstance(exc, (PermissionError, OSError)):
        return MensajeUxError(
            titulo="No se pudo escribir el proyecto en disco",
            mensaje=(
                "No fue posible completar la operación por permisos o almacenamiento. "
                f"ID de incidente: {id_incidente}."
            ),
            causa_probable="Permisos insuficientes, carpeta protegida o falta de espacio en disco.",
            acciones=[
                "Revisa permisos de la carpeta destino.",
                "Cambia la carpeta de salida.",
                "Verifica espacio disponible en disco.",
            ],
            id_incidente=id_incidente,
            detalle_tecnico=_construir_detalle_tecnico(exc, id_incidente),
            ruta_logs=ruta_logs_texto,
        )

    return MensajeUxError(
        titulo="Error inesperado durante la generación",
        mensaje=(
            "Ocurrió un error inesperado. Usa el ID de incidente y revisa los logs para soporte. "
            f"ID de incidente: {id_incidente}."
        ),
        causa_probable="Fallo no contemplado por el flujo normal de generación.",
        acciones=[
            "Copia los detalles para soporte.",
            "Abre la carpeta de logs y adjunta crashes.log.",
            "Reintenta con otra ruta para descartar permisos.",
        ],
        id_incidente=id_incidente,
        detalle_tecnico=_construir_detalle_tecnico(exc, id_incidente),
        ruta_logs=ruta_logs_texto,
    )


def construir_texto_para_copiar(mensaje: MensajeUxError) -> str:
    """Construye el texto completo para la acción 'Copiar detalles'."""
    acciones = "\n".join(f"- {accion}" for accion in mensaje.acciones)
    detalle = mensaje.detalle_tecnico or "Sin detalle técnico disponible."
    ruta_logs = mensaje.ruta_logs or "No disponible"
    causa = mensaje.causa_probable or "No determinada"
    return (
        f"{mensaje.titulo}\n"
        f"ID de incidente: {mensaje.id_incidente}\n"
        f"Mensaje: {mensaje.mensaje}\n"
        f"Causa probable: {causa}\n"
        f"Acciones sugeridas:\n{acciones}\n"
        f"Ruta logs: {ruta_logs}\n\n"
        f"Detalle técnico:\n{detalle}"
    )

