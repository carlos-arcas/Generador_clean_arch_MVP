# Guía de seguridad: gestión de credenciales

## Resumen
El wizard ahora permite capturar credenciales de conexión (usuario + secreto) sin escribirlas en manifiestos ni exponerlas en logs.

## Modos de almacenamiento

1. **Modo seguro recomendado (por defecto)**
   - Las credenciales se usan durante la ejecución actual y no se persisten.
   - Implementado con repositorio en memoria.

2. **Modo persistente opcional en Windows**
   - Si el usuario marca `Guardar credencial en sistema seguro`, se intenta persistir en **Windows Credential Manager** usando `ctypes` (`CredWrite`/`CredRead`/`CredDelete`).
   - Si falla o la plataforma no es Windows, el sistema cae a modo memoria con advertencia.

## Protección en logging
Se incorporó un filtro que sanitiza automáticamente valores sensibles en mensajes de log, cubriendo claves:
- `password`
- `secret`
- `token`
- `api_key`
- `clave`

Ejemplo:
- Entrada: `password=mi_clave token=abcd`
- Persistido: `password=*** token=***`

## Limitaciones
- En sistemas no Windows no hay persistencia nativa del secreto.
- El fallback a memoria implica que los secretos desaparecen al cerrar la aplicación.
- El filtro de logs está orientado a patrones `clave=valor` o `clave:valor`.

## Recomendaciones
- Mantener desmarcada la opción de guardado seguro salvo necesidad operativa.
- Rotar secretos con regularidad.
- Evitar incluir secretos en mensajes manuales de `LOGGER`.
- Auditar periódicamente `logs/seguimiento.log` y `logs/crashes.log`.
