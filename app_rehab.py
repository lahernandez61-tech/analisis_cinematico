import os
from flask import Flask, render_template, request, jsonify
from biomecanica import evaluar_sesion_rehab

app = Flask(__name__)


# Ruta 1: Entrega la interfaz visual (templates/index.html)
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# Ruta 2: API REST que recibe JSON, ejecuta el análisis biomecánico y devuelve JSON
@app.route("/evaluar", methods=["POST"])
def evaluar():
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se recibieron datos válidos en formato JSON."}), 400

    try:
        serie_angulos = str(datos.get("datos", ""))
        fs = float(datos.get("fs", 10))

        resultado = evaluar_sesion_rehab(serie_angulos, fs)
        return jsonify(resultado), 200

    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except Exception as exc:
        return jsonify({"error": f"Error interno en el servidor: {str(exc)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
