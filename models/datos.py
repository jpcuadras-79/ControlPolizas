"""Acceso a datos: único lugar que abre archivos de data/."""

import os
from datetime import datetime

import pandas as pd
import pdfplumber

# Diccionario: etiqueta del PDF -> nombre del campo en el diccionario de salida
CAMPOS = {
    "Numero de poliza": "numero",
    "Ramo": "ramo",
    "Tomador / Asegurado": "nombre",
    "Cedula": "cedula",
    "Vigencia desde": "desde",
    "Vigencia hasta": "hasta",
    "Prima anual": "prima",
    "Forma de pago": "pago",
    "Suma asegurada": "suma",
    "Asesor": "asesor",
}

# Campos que se convierten a fecha
CAMPOS_FECHA = {"desde", "hasta"}

# Campos que se convierten a número
CAMPOS_NUMERO = {"prima", "suma"}


def _texto_a_fecha(texto):
    """Convierte un texto dd/mm/aaaa a objeto date. Devuelve None si está vacío."""
    if not texto or str(texto).strip() == "":
        return None
    return datetime.strptime(str(texto).strip(), "%d/%m/%Y").date()


def _texto_a_numero(texto):
    """Convierte un monto tipo 'CRC 228,000.00' a número float. Devuelve None si está vacío."""
    if not texto or str(texto).strip() == "":
        return None
    limpio = str(texto).strip().replace("CRC", "").replace(",", "").replace(" ", "")
    try:
        return float(limpio)
    except ValueError:
        return None


def cargar_clientes():
    """Lee data/Maestro_Clientes.xlsx (hoja Clientes) con pandas.

    Devuelve el DataFrame con Cedula como texto sin espacios.
    """
    df = pd.read_excel("data/Maestro_Clientes.xlsx", sheet_name="Clientes")
    df["Cedula"] = df["Cedula"].astype(str).str.strip()
    return df


def leer_poliza(ruta_pdf):
    """Abre un PDF de póliza con pdfplumber y devuelve un diccionario con sus datos.

    La primera línea del texto es la aseguradora.
    Las demás líneas con ":" se parsean usando CAMPOS.
    Fechas se convierten a date; montos se convierten a número (None si vacío).
    """
    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        texto = pagina.extract_text() or ""

    lineas = texto.splitlines()
    aseguradora = lineas[0].strip() if lineas else ""

    resultado = {
        "archivo": os.path.basename(ruta_pdf),
        "aseguradora": aseguradora,
        "numero": None,
        "ramo": None,
        "nombre": None,
        "cedula": None,
        "desde": None,
        "hasta": None,
        "prima": None,
        "pago": None,
        "suma": None,
        "asesor": None,
    }

    for linea in lineas[1:]:
        if ":" in linea:
            etiqueta, valor = linea.split(":", 1)
            etiqueta = etiqueta.strip()
            valor = valor.strip()
            if etiqueta in CAMPOS:
                campo = CAMPOS[etiqueta]
                if campo in CAMPOS_FECHA:
                    resultado[campo] = _texto_a_fecha(valor)
                elif campo in CAMPOS_NUMERO:
                    resultado[campo] = _texto_a_numero(valor)
                else:
                    resultado[campo] = valor

    return resultado


def cargar_polizas():
    """Recorre data/polizas en orden alfabético y devuelve lista de diccionarios."""
    carpeta = "data/polizas"
    archivos = sorted(os.listdir(carpeta))
    polizas = []
    for archivo in archivos:
        if archivo.lower().endswith(".pdf"):
            ruta = os.path.join(carpeta, archivo)
            polizas.append(leer_poliza(ruta))
    return polizas
