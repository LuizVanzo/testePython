from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Pegue o token do webhook da variável de ambiente (mais seguro)
WEBHOOK_TOKEN = os.environ.get("WEBHOOK_TOKEN", "8vhpwln0t40oazqsr7xplsgf8umd9cy3")

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    token = request.args.get("auth")

    if token != WEBHOOK_TOKEN:
        return jsonify({"error": "Token inválido"}), 403

    print("Novo negócio recebido:", data)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # Render define a porta via variável de ambiente
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
