from flask import Flask, request, jsonify
import os
import requests
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

WEBHOOK_TOKEN = "8vhpwln0t40oazqsr7xplsgf8umd9cy3"
BITRIX_WEBHOOK_URL = "https://b24-idz4go.bitrix24.com.br/rest/1/qbwi1ie9uhhnehs3"

@app.route("/", methods=["GET"])
def home():
    logger.info("Servidor recebeu uma requisição GET")
    return jsonify({"status": "servidor online"}), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    logger.info("ROTA DE WEBHOOK ACIONADA")
    data = request.json

    # Bitrix pode enviar como form data também
    if data is None:
        data = request.form.to_dict()

    token = request.args.get("auth")

    if token != WEBHOOK_TOKEN:
        return jsonify({"error": "Token inválido"}), 403

    # ⚠️ Substitua pelo nome real do campo "ID Execução" no Bitrix24 (ex: UF_CRM_123456)
    CAMPO_ID_EXECUCAO = "UF_CRM_1773240987269"

    # Pegando dados específicos do negócio
    event = data.get("event", "")
    fields = data.get("data", {}).get("FIELDS", {})
    deal_id = str(fields.get("ID", ""))

    print(f"Evento: {event}", flush=True)
    print(f"ID do negócio: {deal_id}", flush=True)
    print(f"Dados completos: {data}", flush=True)

    if deal_id:
        # Busca os dados completos do negócio para obter o ID Execução
        resp = requests.post(
            f"{BITRIX_WEBHOOK_URL}/crm.deal.get",
            json={"ID": deal_id}
        )
        deal_data = resp.json().get("result", {})
        execution_id = deal_data.get(CAMPO_ID_EXECUCAO, "")

        print(f"ID Execução: {execution_id}", flush=True)

        if execution_id:
            # Busca todos os negócios com o mesmo ID Execução
            resp_list = requests.post(
                f"{BITRIX_WEBHOOK_URL}/crm.deal.list",
                json={
                    "filter": {CAMPO_ID_EXECUCAO: execution_id},
                    "select": ["ID"]
                }
            )
            duplicates = resp_list.json().get("result", [])

            deleted = []
            for dup in duplicates:
                dup_id = str(dup.get("ID", ""))
                if dup_id == deal_id:  # deleta o negócio que disparou o evento, mantém os existentes
                    print(f"Deletando negócio disparador {dup_id} com ID Execução '{execution_id}'", flush=True)
                    requests.post(
                        f"{BITRIX_WEBHOOK_URL}/crm.deal.delete",
                        json={"ID": dup_id}
                    )
                    deleted.append(dup_id)

            if deleted:
                return jsonify({"status": "duplicatas_deletadas", "deal_id": deal_id, "deletados": deleted})

    return jsonify({"status": "ok", "deal_id": deal_id})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
