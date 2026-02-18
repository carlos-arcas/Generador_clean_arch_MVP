import pytest

from dominio.modelos import EntradaManifest, ErrorValidacionDominio, ManifestProyecto


def test_manifest_proyecto_valido() -> None:
    manifest = ManifestProyecto(
        version_generador="0.2.0",
        blueprints_usados=["base_clean_arch@1.0.0"],
        archivos=[EntradaManifest(ruta_relativa="README.md", hash_sha256="abc123")],
        timestamp_generacion="2026-01-01T00:00:00+00:00",
        opciones={"modo": "test"},
    )

    assert manifest.version_generador == "0.2.0"


def test_manifest_detecta_rutas_duplicadas() -> None:
    with pytest.raises(ErrorValidacionDominio, match="duplicadas"):
        ManifestProyecto(
            version_generador="0.2.0",
            blueprints_usados=["base_clean_arch@1.0.0"],
            archivos=[
                EntradaManifest(ruta_relativa="README.md", hash_sha256="a"),
                EntradaManifest(ruta_relativa="README.md", hash_sha256="b"),
            ],
            timestamp_generacion="2026-01-01T00:00:00+00:00",
            opciones={},
        )


def test_entrada_manifest_exige_hash_no_vacio() -> None:
    with pytest.raises(ErrorValidacionDominio, match="hash SHA256"):
        EntradaManifest(ruta_relativa="README.md", hash_sha256="")


def test_manifest_obtener_clases_generadas_desde_rutas() -> None:
    manifest = ManifestProyecto(
        version_generador="0.8.0",
        blueprints_usados=["crud_json@1.0.0"],
        archivos=[
            EntradaManifest(ruta_relativa="dominio/entidades/cliente.py", hash_sha256="a"),
            EntradaManifest(ruta_relativa="dominio/entidades/producto_item.py", hash_sha256="b"),
            EntradaManifest(ruta_relativa="README.md", hash_sha256="c"),
        ],
        timestamp_generacion="2026-01-01T00:00:00+00:00",
        opciones={},
    )

    assert manifest.obtener_clases_generadas() == ["Cliente", "ProductoItem"]
