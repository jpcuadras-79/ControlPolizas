"""Controlador de pólizas: rutas de Flask (Blueprint).

No calcula nada: solo llama a models/ y services/.
"""

import io
import zipfile

from flask import Blueprint, render_template, send_file, abort

from models.polizas import (
    FECHA_CORTE,
    calcular_resultados,
    contar_por_estado,
    primas_por_aseguradora,
    buscar_inconsistencias,
    buscar_por_numero,
)
from services.generador_aviso import crear_aviso_pdf

bp = Blueprint("polizas", __name__)


@bp.route("/")
def inicio():
    """Tablero principal: muestra resultados, conteo, primas, inconsistencias y fecha de corte."""
    resultados = calcular_resultados()
    conteo = contar_por_estado(resultados)
    primas = primas_por_aseguradora(resultados)
    inconsistencias = buscar_inconsistencias(resultados)
    return render_template(
        "inicio.html",
        resultados=resultados,
        conteo=conteo,
        primas=primas,
        inconsistencias=inconsistencias,
        fecha_corte=FECHA_CORTE,
    )


@bp.route("/aviso/<numero>")
def aviso(numero):
    """Devuelve el aviso de renovación en PDF para ver en el navegador.

    404 si la póliza no existe o está Vigente.
    """
    poliza = buscar_por_numero(numero)
    if poliza is None:
        abort(404)
    if poliza["estado"] == "Vigente":
        abort(404)

    pdf_bytes = crear_aviso_pdf(poliza)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"aviso_{numero}.pdf",
    )


@bp.route("/descargar-avisos")
def descargar_avisos():
    """Arma en memoria un .zip con los avisos de pólizas Por vencer y Vencidas."""
    resultados = calcular_resultados()

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in resultados:
            if r["estado"] in ("Por vencer", "Vencida"):
                pdf_bytes = crear_aviso_pdf(r)
                zf.writestr(f"aviso_{r['numero']}.pdf", pdf_bytes)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="avisos.zip",
    )
