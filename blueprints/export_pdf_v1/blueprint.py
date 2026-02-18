"""Blueprint para exportación tabular en PDF básico (reportlab)."""

from __future__ import annotations

from dataclasses import dataclass
import textwrap

from aplicacion.puertos.blueprint import Blueprint
from dominio.especificacion import EspecificacionClase, EspecificacionProyecto, ErrorValidacionDominio
from dominio.plan_generacion import ArchivoGenerado, PlanGeneracion


@dataclass(frozen=True)
class NombresClase:
    nombre_clase: str
    nombre_snake: str
    nombre_plural: str


class ExportPdfBlueprint(Blueprint):
    def nombre(self) -> str:
        return "export_pdf"

    def version(self) -> str:
        return "1.0.0"

    def validar(self, especificacion: EspecificacionProyecto) -> None:
        especificacion.validar()
        if not especificacion.clases:
            raise ErrorValidacionDominio(
                "El blueprint export_pdf requiere al menos una clase en la especificación."
            )

    def generar_plan(self, especificacion: EspecificacionProyecto) -> PlanGeneracion:
        self.validar(especificacion)

        archivos: list[ArchivoGenerado] = [
            ArchivoGenerado(
                "aplicacion/puertos/exportadores/exportador_tabular_pdf.py",
                self._contenido_puerto_exportador(),
            ),
            ArchivoGenerado(
                "infraestructura/informes/pdf/exportador_pdf_reportlab.py",
                self._contenido_exportador_pdf(),
            ),
            ArchivoGenerado(
                "tests/infraestructura/test_export_pdf.py",
                self._contenido_test_exportador_pdf(),
            ),
        ]

        for clase in especificacion.clases:
            nombres = self._construir_nombres(clase)
            archivos.append(
                ArchivoGenerado(
                    f"aplicacion/casos_uso/informes/generar_informe_{nombres.nombre_plural}_pdf.py",
                    self._contenido_caso_uso_informe(clase, nombres),
                )
            )

        plan = PlanGeneracion(archivos=archivos)
        plan.validar_sin_conflictos()
        return plan

    def _construir_nombres(self, clase: EspecificacionClase) -> NombresClase:
        nombre_snake = self._pascal_a_snake(clase.nombre)
        return NombresClase(
            nombre_clase=clase.nombre,
            nombre_snake=nombre_snake,
            nombre_plural=self._pluralizar(nombre_snake),
        )

    def _pascal_a_snake(self, texto: str) -> str:
        caracteres: list[str] = []
        for indice, caracter in enumerate(texto):
            if caracter.isupper() and indice > 0:
                caracteres.append("_")
            caracteres.append(caracter.lower())
        return "".join(caracteres)

    def _pluralizar(self, nombre: str) -> str:
        if nombre.endswith(("a", "e", "i", "o", "u")):
            return f"{nombre}s"
        if nombre.endswith("s"):
            return nombre
        return f"{nombre}es"

    def _contenido_puerto_exportador(self) -> str:
        return textwrap.dedent(
            '''\
            """Puerto de exportación tabular para PDF."""

            from __future__ import annotations

            from abc import ABC, abstractmethod


            class ExportadorTabularPdf(ABC):
                @abstractmethod
                def exportar(self, ruta: str, encabezados: list[str], filas: list[list[str]], titulo: str) -> None:
                    """Exporta un informe tabular hacia un PDF básico."""
            '''
        )

    def _contenido_caso_uso_informe(self, clase: EspecificacionClase, nombres: NombresClase) -> str:
        columnas = ["id", *[atributo.nombre for atributo in clase.atributos if atributo.nombre != "id"]]
        titulo = f"Informe de {nombres.nombre_plural.capitalize()}"
        return textwrap.dedent(
            f'''\
            """Caso de uso para generar informe PDF de {nombres.nombre_plural}."""

            from __future__ import annotations

            import logging

            from aplicacion.puertos.exportadores.exportador_tabular_pdf import ExportadorTabularPdf
            from aplicacion.puertos.repositorio_{nombres.nombre_snake} import Repositorio{nombres.nombre_clase}

            LOGGER = logging.getLogger(__name__)


            class GenerarInforme{nombres.nombre_clase}Pdf:
                def __init__(
                    self,
                    repositorio: Repositorio{nombres.nombre_clase},
                    exportador: ExportadorTabularPdf,
                ) -> None:
                    self._repositorio = repositorio
                    self._exportador = exportador
                    self._encabezados = {columnas!r}
                    self._titulo = {titulo!r}

                def ejecutar(self, ruta_salida: str) -> str:
                    entidades = self._repositorio.listar()
                    filas = [
                        [str(getattr(entidad, columna, "")) for columna in self._encabezados]
                        for entidad in entidades
                    ]
                    self._exportador.exportar(
                        ruta=ruta_salida,
                        encabezados=self._encabezados,
                        filas=filas,
                        titulo=self._titulo,
                    )
                    LOGGER.info("Informe PDF generado en %s", ruta_salida)
                    return ruta_salida
            '''
        )

    def _contenido_exportador_pdf(self) -> str:
        return textwrap.dedent(
            '''\
            """Exportador PDF básico con paginación mínima."""

            from __future__ import annotations

            from pathlib import Path

            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            from aplicacion.puertos.exportadores.exportador_tabular_pdf import ExportadorTabularPdf


            class ExportadorPdfReportlab(ExportadorTabularPdf):
                def exportar(self, ruta: str, encabezados: list[str], filas: list[list[str]], titulo: str) -> None:
                    destino = Path(ruta)
                    destino.parent.mkdir(parents=True, exist_ok=True)

                    documento = canvas.Canvas(str(destino), pagesize=A4)
                    ancho, alto = A4
                    margen_x = 40
                    y = alto - 50
                    salto_linea = 18

                    documento.setFont("Helvetica-Bold", 12)
                    documento.drawString(margen_x, y, titulo)
                    y -= salto_linea * 2

                    documento.setFont("Helvetica-Bold", 10)
                    documento.drawString(margen_x, y, " | ".join(encabezados))
                    y -= salto_linea

                    documento.setFont("Helvetica", 10)
                    for fila in filas:
                        if y < 50:
                            documento.showPage()
                            y = alto - 50
                            documento.setFont("Helvetica-Bold", 10)
                            documento.drawString(margen_x, y, " | ".join(encabezados))
                            y -= salto_linea
                            documento.setFont("Helvetica", 10)
                        documento.drawString(margen_x, y, " | ".join(fila))
                        y -= salto_linea

                    documento.save()
            '''
        )

    def _contenido_test_exportador_pdf(self) -> str:
        return textwrap.dedent(
            '''\
            from pathlib import Path

            from infraestructura.informes.pdf.exportador_pdf_reportlab import ExportadorPdfReportlab


            def test_exportador_pdf_generar_archivo_basico(tmp_path: Path) -> None:
                ruta = tmp_path / "clientes.pdf"

                ExportadorPdfReportlab().exportar(
                    ruta=str(ruta),
                    encabezados=["id", "nombre"],
                    filas=[["1", "Ana"]],
                    titulo="Informe de Clientes",
                )

                assert ruta.exists()
                assert ruta.stat().st_size > 0
            '''
        )
