# %%
from flask import Flask, render_template, request, jsonify
import geopandas as gpd
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

DATA_PATH = "data/data.geojson"
gdf = gpd.read_file(DATA_PATH)

gdf["timestamp"] = pd.to_datetime(gdf["timestamp"])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/filter", methods=["GET"])
def filter_data():
    start_str = request.args.get("start")
    end_str = request.args.get("end")

    try:
        start = pd.to_datetime(start_str)
        end = pd.to_datetime(end_str)
    except Exception as e:
        return jsonify({"error": "Invalid date format"}), 400

    filtered = gdf[(gdf["timestamp"] >= start) & (gdf["timestamp"] <= end)].copy()
    filtered["timestamp"] = filtered["timestamp"].dt.strftime("%Y-%m-%d")

    return jsonify(filtered.to_crs(epsg=4326).to_json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

# %%
