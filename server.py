# server.py
from flask import Flask, request, jsonify

app = Flask(__name__)
servers = []

@app.route("/add_server", methods=["POST"])
def add_server():
    data = request.json
    # Remove servidores antigos com mesmo IP
    servers[:] = [s for s in servers if s["ip"] != data["ip"]]
    servers.append(data)
    return jsonify({"status": "ok"})

@app.route("/servers", methods=["GET"])
def get_servers():
    return jsonify(servers)

@app.route("/clear", methods=["POST"])
def clear():
    servers.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
