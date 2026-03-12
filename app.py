from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

WEBHOOK_TOKEN = "8vhpwln0t40oazqsr7xplsgf8umd9cy3"
BITRIX_WEBHOOK_URL = "https://b24-idz4go.bitrix24.com.br/rest/1/qbwi1ie9uhhnehs3"

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "servidor online"}), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Bitrix pode enviar como form data também
    if data is None:
        data = request.form.to_dict()

    token = request.args.get("auth")

    if token != WEBHOOK_TOKEN:
        return jsonify({"error": "Token inválido"}), 403

    # Pegando dados específicos do negócio
    event = data.get("event", "")
    fields = data.get("data", {}).get("FIELDS", {})
    deal_id = fields.get("ID", "")

    print(f"Evento: {event}", flush=True)
    print(f"ID do negócio: {deal_id}", flush=True)
    print(f"Dados completos: {data}", flush=True)

    if deal_id:
        resp = requests.post(
            f"{BITRIX_WEBHOOK_URL}/crm.deal.get",
            json={"ID": deal_id}
        )
        result = resp.json()

        if result.get("result"):  # negociação já existe no Bitrix
            print(f"Negociação {deal_id} já existe. Deletando...", flush=True)
            requests.post(
                f"{BITRIX_WEBHOOK_URL}/crm.deal.delete",
                json={"ID": deal_id}
            )
            return jsonify({"status": "deletado", "deal_id": deal_id})

    return jsonify({"status": "ok", "deal_id": deal_id})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
