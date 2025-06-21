# %%
import json
import os
from flask import Flask, jsonify, send_from_directory, request

from utils import add_time

app = Flask(__name__)


@app.route("/api/geojson")
def geojson():
    time_filter = request.args.get("time")
    with open("./geojson/cityhall.geojson") as f:
        gj = json.load(f)
        gj = add_time(gj)

    if time_filter:
        features = [
            f for f in gj["features"] if f["properties"].get("time") == time_filter
        ]
        gj["features"] = features
    return jsonify(gj)


@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "index.html")


@app.route("/app.js")
def serve_js():
    return send_from_directory("../frontend", "app.js")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

# %%
