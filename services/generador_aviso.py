"""Generador de avisos de renovación en PDF (A4 vertical)."""

from io import BytesIO

from fpdf import FPDF

COLOR_ROJO = (174, 24, 0)      # #AE1800
COLOR_GRIS = (200, 200, 200)   # gris claro para pie de página
COLOR_NEGRO = (32, 30, 29)     # #201E1D


def _latin1(texto):
    """Convierte texto a latin-1 para evitar errores con Helvetica en fpdf2."""
    if texto is None:
        return ""
    return str(texto).encode("latin-1", errors="replace").decode("latin-1")


def crear_aviso_pdf(poliza):
    """Crea un aviso de renovación en PDF (A4 vertical) y lo devuelve en bytes.

    Recibe un diccionario de póliza con campos como:
    nombre, estado, hasta, dias_hasta_vencer, asesor, numero, aseguradora,
    ramo, cedula, desde, prima, pago.
    """
    nombre = poliza.get("nombre") or "cliente"
    estado = poliza.get("estado") or "Sin fecha"
    hasta = poliza.get("hasta")
    dias = poliza.get("dias_hasta_vencer")
    asesor = poliza.get("asesor") or ""

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- Banda superior roja ---
    pdf.set_fill_color(*COLOR_ROJO)
    pdf.rect(0, 0, 210, 30, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(10, 8)
    pdf.cell(0, 8, _latin1("Corredora de Seguros Horizonte"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, _latin1("Aviso de renovación de póliza"), ln=True)
    pdf.ln(5)

    # --- Saludo ---
    pdf.set_text_color(*COLOR_NEGRO)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, _latin1(f"Estimado(a) {nombre}:"), ln=True)
    pdf.ln(3)

    # --- Párrafo distinto según estado ---
    if estado == "Vencida":
        fecha_str = hasta.strftime("%d/%m/%Y") if hasta else "fecha desconocida"
        pdf.multi_cell(0, 6, _latin1(
            f"Su póliza número {poliza.get('numero', '')} venció el {fecha_str}. "
            "Por favor, renueve su póliza lo antes posible para mantener su cobertura activa."
        ))
    elif estado == "Por vencer":
        dias_str = str(dias) if dias is not None else "desconocido"
        fecha_hasta = hasta.strftime("%d/%m/%Y") if hasta else ""
        pdf.multi_cell(0, 6, _latin1(
            f"Su póliza número {poliza.get('numero', '')} vence el {fecha_hasta} "
            f"en {dias_str} días. Su asesor {asesor} se comunicará con usted para coordinar la renovación."
        ))
    else:
        pdf.multi_cell(0, 6, _latin1(
            f"Su póliza número {poliza.get('numero', '')} está vigente. "
            "Gracias por confiar en la Corredora de Seguros Horizonte."
        ))
    pdf.ln(5)

    # --- Tabla de datos ---
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(40, 7, _latin1("Campo"), border=1, fill=True)
    pdf.cell(0, 7, _latin1("Valor"), border=1, fill=True, ln=True)

    filas = [
        ("Número de póliza", poliza.get("numero", "")),
        ("Aseguradora", poliza.get("aseguradora", "")),
        ("Ramo", poliza.get("ramo", "")),
        ("Cédula", poliza.get("cedula", "")),
        (
            "Vigencia",
            f"{poliza.get('desde').strftime('%d/%m/%Y') if poliza.get('desde') else ''} al "
            f"{poliza.get('hasta').strftime('%d/%m/%Y') if poliza.get('hasta') else ''}",
        ),
        (
            "Prima anual",
            f"CRC {poliza.get('prima'):,.2f}" if poliza.get('prima') is not None else "No registrada",
        ),
        ("Forma de pago", poliza.get("pago", "")),
    ]

    pdf.set_font("Helvetica", "", 10)
    for campo, valor in filas:
        pdf.cell(40, 7, _latin1(campo), border=1)
        pdf.cell(0, 7, _latin1(str(valor)), border=1, ln=True)

    pdf.ln(10)

    # --- Pie de página en gris ---
    pdf.set_text_color(*COLOR_GRIS)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 6, _latin1("Documento ficticio con fines académicos."), ln=True, align="C")

    # Devolver bytes
    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
