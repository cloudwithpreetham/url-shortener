import os
import string
import random

from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import redis
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
CORS(app)

metrics = PrometheusMetrics(app)

# Redis connection (configurable via env vars for Docker/K8s)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

r = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
)

CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits


def generate_code(length=CODE_LENGTH):
    return "".join(random.choices(ALPHABET, k=length))


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint - useful for Kubernetes liveness/readiness probes."""
    try:
        r.ping()
        return jsonify({"status": "ok", "redis": "connected"}), 200
    except redis.exceptions.ConnectionError:
        return jsonify({"status": "error", "redis": "disconnected"}), 503


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json(silent=True) or {}
    long_url = data.get("url", "").strip()

    if not long_url:
        return jsonify({"error": "Missing 'url' in request body"}), 400

    if not (long_url.startswith("http://") or long_url.startswith("https://")):
        long_url = "https://" + long_url

    # Loop (not a single check) because two calls could generate the
    # same 6-char code by chance; keep drawing until we find one that
    # is not already a key in Redis.
    code = generate_code()
    while r.exists(f"url:{code}"):
        code = generate_code()

    r.set(f"url:{code}", long_url)

    base_url = request.host_url.rstrip("/")
    return jsonify({
        "code": code,
        "short_url": f"{base_url}/{code}",
        "long_url": long_url
    }), 201


@app.route("/<code>", methods=["GET"])
def resolve(code):
    long_url = r.get(f"url:{code}")
    if not long_url:
        return jsonify({"error": "Short URL not found"}), 404
    return redirect(long_url, code=302)


@app.route("/stats/<code>", methods=["GET"])
def stats(code):
    long_url = r.get(f"url:{code}")
    if not long_url:
        return jsonify({"error": "Short URL not found"}), 404
    return jsonify({"code": code, "long_url": long_url}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
