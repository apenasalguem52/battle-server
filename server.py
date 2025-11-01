import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Lista em memória: cada item = { name, ip, port, last_seen (ISO str) }
servers = []

# TTL: tempo que um servidor fica na lista sem atualizar (em segundos)
SERVER_TTL = int(os.environ.get("SERVER_TTL_SECONDS", 300))  # 5 minutos por padrão

def prune_servers():
    """Remove servidores que não atualizaram dentro do TTL."""
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=SERVER_TTL)
    servers[:] = [s for s in servers if datetime.fromisoformat(s["last_seen"]) >= cutoff]

@app.route("/add_server", methods=["POST"])
def add_server():
    data = request.get_json(force=True)
    # dados esperados: name, ip, port
    if not data or "name" not in data or "ip" not in data or "port" not in data:
        return jsonify({"error": "payload inválido; enviar name, ip, port"}), 400

    prune_servers()
    # atualiza (by ip+port) ou adiciona
    for s in servers:
        if s["ip"] == data["ip"] and int(s["port"]) == int(data["port"]):
            s["name"] = data["name"]
            s["last_seen"] = datetime.utcnow().isoformat()
            return jsonify({"status": "updated"})
    # novo servidor
    servers.append({
        "name": data["name"],
        "ip": data["ip"],
        "port": int(data["port"]),
        "last_seen": datetime.utcnow().isoformat()
    })
    return jsonify({"status": "added"})

@app.route("/servers", methods=["GET"])
def get_servers():
    prune_servers()
    return jsonify(servers)

@app.route("/remove_server", methods=["POST"])
def remove_server():
    data = request.get_json(force=True)
    if not data or "ip" not in data or "port" not in data:
        return jsonify({"error": "payload inválido; enviar ip, port"}), 400
    servers[:] = [s for s in servers if not (s["ip"] == data["ip"] and int(s["port"]) == int(data["port"]))]
    return jsonify({"status": "removed"})

if __name__ == "__main__":
    # Render fornece a porta via ENV variable "$PORT"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
