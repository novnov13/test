from flask import Flask, render_template, request, jsonify
import geojson
import networkx as nx
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

    data = geojson.load(file)

    coordinates = []
    names = []
    for feature in data['features']:
        coords = feature['geometry']['coordinates']
        name = feature['properties']['P11_001']  # GeoJSONのプロパティ名に合わせて変更してください
        coordinates.append(coords)
        names.append(name)

    points = np.array(coordinates)
    triangulation = Delaunay(points)

    G = nx.Graph()

    # 辺と重み（距離）を追加
    for simplex in triangulation.simplices:
        for i in range(3):
            for j in range(i + 1, 3):
                node1 = names[simplex[i]]
                node2 = names[simplex[j]]
                dist = np.linalg.norm(points[simplex[i]] - points[simplex[j]])
                G.add_edge(node1, node2, weight=dist)

    # 中心性計算（距離を重みとして使うのはclosenessのみ）
    if centrality_type == "degree":
        centralities = nx.degree_centrality(G)
    elif centrality_type == "closeness":
        centralities = nx.closeness_centrality(G, distance="weight")
    else:
        centralities = nx.degree_centrality(G)

    nodes = []
    for n in G.nodes():
        idx = names.index(n)
        nodes.append({
            "id": n,
            "centrality": float(centralities.get(n, 0)),
            "x": float(points[idx][0]),
            "y": float(points[idx][1])
        })

    links = []
    for u, v, data_edge in G.edges(data=True):
        links.append({
            "source": u,
            "target": v,
            "distance": float(data_edge.get("weight", 0))
        })

    return jsonify({"nodes": nodes, "links": links})

if __name__ == "__main__":
    app.run(debug=True)
