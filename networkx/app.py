from flask import Flask, render_template, request, jsonify
import networkx as nx
import pandas as pd
import json
import geojson
import numpy as np
from scipy.spatial import Delaunay

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload_geojson", methods=["POST"])
def upload_geojson():
    file = request.files["file"]
    centrality_type = request.form.get("centrality", "degree")

    # GeoJSONファイルの読み込み
    data = geojson.load(file)

    # 座標とノード名の抽出
    coordinates = []
    names = []
    for feature in data['features']:
        coords = feature['geometry']['coordinates']
        name = feature['properties']['P11_001']  # ノード名（適宜変更）
        coordinates.append(coords)
        names.append(name)

    # TIN（三角形分割）による接続の構築
    points = np.array(coordinates)
    triangulation = Delaunay(points)

    # NetworkX グラフの作成
    G = nx.Graph()

    for simplex in triangulation.simplices:
        for i in range(3):
            for j in range(i + 1, 3):
                node1 = names[simplex[i]]
                node2 = names[simplex[j]]
                dist = np.linalg.norm(points[simplex[i]] - points[simplex[j]])
                G.add_edge(node1, node2, weight=dist)

    # 中心性計算（次数中心性と近接中心性）
    centralities = {
        "degree": nx.degree_centrality(G),
        "closeness": nx.closeness_centrality(G)
    }

    # グラフのデータをJSON形式に変換
    data = {
        "nodes": [
            {
                "id": str(n),
                "centrality": {
                    "degree": float(centralities["degree"].get(n, 0)),
                    "closeness": float(centralities["closeness"].get(n, 0))
                }
            } for n in G.nodes()
        ],
        "links": [
            {"source": str(u), "target": str(v), "distance": data["weight"]}
            for u, v, data in G.edges(data=True)
        ]
    }

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
