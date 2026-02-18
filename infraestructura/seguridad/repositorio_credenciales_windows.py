"""Repositorio de credenciales usando Windows Credential Manager vía ctypes."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import sys

from dominio.seguridad.credencial import Credencial

if sys.platform.startswith("win"):
    CRED_TYPE_GENERIC = 1
    CRED_PERSIST_LOCAL_MACHINE = 2

    class CREDENTIALW(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

    PCREDENTIALW = ctypes.POINTER(CREDENTIALW)


class RepositorioCredencialesWindows:
    """Adaptador para almacenar credenciales en el gestor nativo de Windows."""

    def __init__(self) -> None:
        if not sys.platform.startswith("win"):
            raise OSError("RepositorioCredencialesWindows solo está disponible en Windows.")

        self._advapi32 = ctypes.windll.advapi32
        self._cred_write = self._advapi32.CredWriteW
        self._cred_write.argtypes = [ctypes.POINTER(CREDENTIALW), wintypes.DWORD]
        self._cred_write.restype = wintypes.BOOL

        self._cred_read = self._advapi32.CredReadW
        self._cred_read.argtypes = [wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(PCREDENTIALW)]
        self._cred_read.restype = wintypes.BOOL

        self._cred_delete = self._advapi32.CredDeleteW
        self._cred_delete.argtypes = [wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
        self._cred_delete.restype = wintypes.BOOL

        self._cred_free = self._advapi32.CredFree
        self._cred_free.argtypes = [ctypes.c_void_p]
        self._cred_free.restype = None

    def guardar(self, credencial: Credencial) -> None:
        secret_bytes = credencial.secreto.encode("utf-16-le")
        blob = (ctypes.c_ubyte * len(secret_bytes)).from_buffer_copy(secret_bytes)

        registro = CREDENTIALW()
        registro.Flags = 0
        registro.Type = CRED_TYPE_GENERIC
        registro.TargetName = credencial.identificador
        registro.CredentialBlobSize = len(secret_bytes)
        registro.CredentialBlob = ctypes.cast(blob, ctypes.POINTER(ctypes.c_ubyte))
        registro.Persist = CRED_PERSIST_LOCAL_MACHINE
        registro.AttributeCount = 0
        registro.Attributes = None
        registro.TargetAlias = None
        registro.UserName = credencial.usuario
        registro.Comment = credencial.tipo

        if not self._cred_write(ctypes.byref(registro), 0):
            raise OSError(f"No se pudo guardar credencial en Windows. Código={ctypes.GetLastError()}")

    def obtener(self, identificador: str) -> Credencial | None:
        puntero = PCREDENTIALW()
        ok = self._cred_read(identificador, CRED_TYPE_GENERIC, 0, ctypes.byref(puntero))
        if not ok:
            codigo = ctypes.GetLastError()
            if codigo in (1168, 2):
                return None
            raise OSError(f"No se pudo leer credencial en Windows. Código={codigo}")

        try:
            cred = puntero.contents
            secreto = bytes(cred.CredentialBlob[: cred.CredentialBlobSize]).decode("utf-16-le")
            usuario = cred.UserName or ""
            tipo = cred.Comment or "GENERICA"
            return Credencial(identificador=identificador, usuario=usuario, secreto=secreto, tipo=tipo)
        finally:
            self._cred_free(puntero)

    def eliminar(self, identificador: str) -> None:
        ok = self._cred_delete(identificador, CRED_TYPE_GENERIC, 0)
        if not ok:
            codigo = ctypes.GetLastError()
            if codigo in (1168, 2):
                return
            raise OSError(f"No se pudo eliminar credencial en Windows. Código={codigo}")
