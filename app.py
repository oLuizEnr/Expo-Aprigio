from flask import Flask, request, jsonify, render_template
from threading import Lock

app = Flask(__name__, static_folder='static', template_folder='templates')

# variável global protegida por lock para armazenar a última tensão recebida
tensao_atual = {"value": 0.0}
lock = Lock()

@app.route("/")
def index():
    # renderiza o HTML com o valor atual (caso queira aparecer na renderização inicial)
    with lock:
        t = tensao_atual["value"]
    return render_template("index.html", tensao=t)

@app.route("/api/tensao", methods=["POST"])
def receber_tensao():
    """
    Endpoint que o ESP vai chamar com JSON:
    { "tensao": 4.32 }
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    t = data.get("tensao")
    if t is None:
        return jsonify({"error": "campo 'tensao' ausente"}), 400

    try:
        t = float(t)
    except:
        return jsonify({"error": "valor de 'tensao' inválido"}), 400

    with lock:
        tensao_atual["value"] = t

    # opcional: log no servidor
    app.logger.info(f"Tensão recebida: {t} V")
    return jsonify({"status": "ok", "tensao": t})

@app.route("/api/tensao-atual", methods=["GET"])
def tensao_atual_api():
    """Endpoint que o front pode consultar periodicamente via fetch()"""
    with lock:
        t = tensao_atual["value"]
    return jsonify({"tensao": t})

if __name__ == "__main__":
    # para execução local (dev)
    app.run(host="0.0.0.0", port=5000, debug=True)