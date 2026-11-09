"""Reglas del negocio para el control de pólizas."""

from datetime import date

from models.datos import cargar_clientes, cargar_polizas

FECHA_CORTE = date(2026, 11, 9)
DIAS_AVISO = 30


def estado_poliza(hasta, fecha_corte=FECHA_CORTE):
    """Devuelve el estado de una póliza.

    Reglas:
    - Sin fecha: hasta es None.
    - Vencida: hasta < fecha_corte.
    - Por vencer: 0 <= días hasta vencer <= DIAS_AVISO.
    - Vigente: más de DIAS_AVISO días.
    """
    if hasta is None:
        return "Sin fecha"
    dias = (hasta - fecha_corte).days
    if dias < 0:
        return "Vencida"
    if 0 <= dias <= DIAS_AVISO:
        return "Por vencer"
    return "Vigente"


def calcular_resultados(fecha_corte=FECHA_CORTE):
    """Cruza cada póliza con el maestro por cédula.

    Añade a cada diccionario: correo, en_maestro, dias_hasta_vencer y estado.
    Devuelve lista ordenada de menos a más días (lo urgente primero).
    """
    clientes_df = cargar_clientes()
    clientes_por_cedula = {}
    for _, fila in clientes_df.iterrows():
        clientes_por_cedula[fila["Cedula"]] = {
            "correo": fila["Correo"],
        }

    polizas = cargar_polizas()
    resultados = []
    for p in polizas:
        info = clientes_por_cedula.get(p["cedula"])
        en_maestro = info is not None
        correo = info["correo"] if en_maestro else None

        dias_hasta_vencer = None
        if p["hasta"] is not None:
            dias_hasta_vencer = (p["hasta"] - fecha_corte).days

        estado = estado_poliza(p["hasta"], fecha_corte)

        resultados.append({
            **p,
            "correo": correo,
            "en_maestro": en_maestro,
            "dias_hasta_vencer": dias_hasta_vencer,
            "estado": estado,
        })

    resultados.sort(
        key=lambda r: r["dias_hasta_vencer"] if r["dias_hasta_vencer"] is not None else float("inf")
    )
    return resultados


def contar_por_estado(resultados):
    """Devuelve diccionario con cuántas pólizas hay de cada estado."""
    conteo = {}
    for r in resultados:
        estado = r["estado"]
        conteo[estado] = conteo.get(estado, 0) + 1
    return conteo


def primas_por_aseguradora(resultados):
    """Devuelve diccionario aseguradora -> suma de primas no vencidas.

    Ordenado de mayor a menor suma.
    """
    primas = {}
    for r in resultados:
        if r["estado"] != "Vencida" and r["prima"] is not None:
            aseguradora = r["aseguradora"]
            primas[aseguradora] = primas.get(aseguradora, 0) + r["prima"]
    return dict(sorted(primas.items(), key=lambda item: item[1], reverse=True))


def buscar_inconsistencias(resultados):
    """Devuelve lista de textos con los 3 tipos de problema de AGENTS.md.

    1. Cliente del maestro sin ninguna póliza.
    2. Póliza cuya cédula no está en el maestro.
    3. Póliza sin prima o con fecha ilegible.
    """
    inconsistencias = []

    clientes_df = cargar_clientes()
    cedulas_con_poliza = set()
    for r in resultados:
        if r["en_maestro"] and r["cedula"]:
            cedulas_con_poliza.add(r["cedula"])

    # (1) cliente del maestro sin ninguna póliza
    for _, fila in clientes_df.iterrows():
        cedula = fila["Cedula"]
        if cedula not in cedulas_con_poliza:
            inconsistencias.append(
                f"Cliente sin póliza: {fila['Nombre_Completo']} (Cédula: {cedula})"
            )

    # (2) póliza cuya cédula no está en el maestro
    for r in resultados:
        if not r["en_maestro"] and r["cedula"]:
            inconsistencias.append(
                f"Póliza con cédula no registrada: {r['numero']} (Cédula: {r['cedula']})"
            )

    # (3) póliza sin prima o con fecha ilegible
    for r in resultados:
        if r["prima"] is None:
            inconsistencias.append(f"Póliza sin prima: {r['numero']}")
        if r["hasta"] is None:
            inconsistencias.append(f"Póliza con fecha ilegible: {r['numero']}")

    return inconsistencias


def buscar_por_numero(numero):
    """Busca una póliza por su número en los resultados calculados."""
    resultados = calcular_resultados()
    for r in resultados:
        if r["numero"] == numero:
            return r
    return None
