from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return """
    <!doctype html>
    <html lang="es">
      <head><meta charset="utf-8"><title>Hola desde Flask</title></head>
      <body style="font-family: sans-serif;">
        <h1>¡Hola, Russell! 🚀</h1>
        <p>Esta página está servida por Flask dentro de Docker.</p>
        <p>Ruta de salud: <a href="/healthz">/healthz</a></p>
      </body>
    </html>
    """

@app.get("/healthz")
def healthz():
    # End-point de salud para el HEALTHCHECK del contenedor
    return jsonify(status="ok", app="flask", version="1")

# Nota: en producción lanzaremos con gunicorn; este main permite ejecutar "python app.py" localmente si quisieras
if __name__ == "__main__":
    # host 0.0.0.0 -> escucha en todas las interfaces (requisito para acceder desde fuera del contenedor)
    app.run(host="0.0.0.0", port=8000, debug=False)
