"""Controlador de pólizas: rutas de Flask (Blueprint).

No calcula nada: solo llama a models/ y services/.
"""

import io
import zipfile

import pandas as pd

from flask import Blueprint, render_template, send_file, abort, request, session, redirect, url_for, flash

from models.datos import cargar_clientes_desde_archivo
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
    """Tablero principal: muestra resultados, conteo, primas, inconsistencias y fecha de corte.

    Si hay un maestro de clientes importado en la sesión, lo usa; si no, carga el de data/.
    """
    clientes_data = session.get("clientes_df")
    clientes_df = pd.DataFrame(clientes_data) if clientes_data else None
    resultados = calcular_resultados(clientes_df=clientes_df)
    conteo = contar_por_estado(resultados)
    primas = primas_por_aseguradora(resultados)
    inconsistencias = buscar_inconsistencias(resultados, clientes_df=clientes_df)
    return render_template(
        "inicio.html",
        resultados=resultados,
        conteo=conteo,
        primas=primas,
        inconsistencias=inconsistencias,
        fecha_corte=FECHA_CORTE,
    )


@bp.route("/importar-clientes", methods=["POST"])
def importar_clientes():
    """Recibe un archivo Excel subido, lo procesa y lo guarda en la sesión para usarlo como maestro de clientes.

    Variables:
        request.files['archivo']: archivo Excel subido por el usuario.
    Redirige al tablero con mensaje de éxito o error.
    """
    if "archivo" not in request.files:
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for("polizas.inicio"))

    archivo = request.files["archivo"]

    if archivo.filename == "":
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for("polizas.inicio"))

    if not (archivo.filename.lower().endswith(".xlsx") or archivo.filename.lower().endswith(".xls")):
        flash("El archivo debe ser de Excel (.xlsx o .xls).", "error")
        return redirect(url_for("polizas.inicio"))

    try:
        clientes_df = cargar_clientes_desde_archivo(archivo)
        # Guardamos el DataFrame en la sesión como diccionario para serializarlo
        session["clientes_df"] = clientes_df.to_dict(orient="records")
        flash(f"Maestro de clientes importado correctamente: {archivo.filename}", "exito")
    except Exception as e:
        flash(f"Error al procesar el archivo: {str(e)}", "error")

    return redirect(url_for("polizas.inicio"))


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
