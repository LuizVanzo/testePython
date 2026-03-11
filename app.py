from flask import Flask, request, jsonify

app = Flask(__name__)

# Token configurado no webhook do Bitrix24
WEBHOOK_TOKEN = "5y1ab8rlb3q6n90y6l5sk0ap1swjq5y3"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    token = request.args.get("auth")  # Se o token vier como query param

    # Verifica se o token confere
    if token != WEBHOOK_TOKEN:
        return jsonify({"error": "Token inválido"}), 403

    # Aqui você recebe os dados do evento 'Deal created'
    print("Novo negócio recebido:")
    print(data)

    # Você pode processar os dados, salvar no banco, enviar email, etc.
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Executa na porta 5000, acessível via http://192.168.0.100:5000
    app.run(host="0.0.0.0", port=5000)
