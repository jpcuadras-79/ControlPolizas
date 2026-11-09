"""Punto de entrada de la aplicación Flask."""

from flask import Flask

from controllers.polizas_controller import bp

app = Flask(
    __name__,
    template_folder="views",
    static_folder="public/static",
    static_url_path="/static",
)

app.register_blueprint(bp)


@app.template_filter("fecha")
def filtro_fecha(fecha):
    """Formatea una fecha como dd/mm/aaaa o devuelve '—' si es None."""
    if fecha is None:
        return "—"
    return fecha.strftime("%d/%m/%Y")


@app.template_filter("monto")
def filtro_monto(valor):
    """Formatea un monto como CRC X,XXX.XX o devuelve 'No registrada' si es None."""
    if valor is None:
        return "No registrada"
    return f"CRC {valor:,.2f}"


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
