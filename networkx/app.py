from flask import Flask, render_template, request, jsonify
import geojson
import networkx as nx
import numpy as np
from scipy.spatial import Delaunay

app = Flask(__name__)

# グローバルデータ保持
original_data = {
    "points": [],
    "names": [],
    "edges": []
}

def normalize_distances(edges, new_min=10, new_max=100):
    distances = [d for _, _, d in edges]
    old_min = min(distances)
    old_max = max(distances)
    if old_max == old_min:
        # 全て同じ距離なら固定値を返す
        return [(u, v, (new_min + new_max)/2) for u, v, d in edges]
    normalized_edges = []
    for u, v, d in edges:
        # 線形スケーリング
        norm_d = new_min + (d - old_min) * (new_max - new_min) / (old_max - old_min)
        normalized_edges.append((u, v, norm_d))
    return normalized_edges

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload_geojson", methods=["POST"])
def upload_geojson():
    global original_data

    file = request.files["file"]
    centrality_type = request.form.get("centrality", "degree")

    data = geojson.load(file)

    coordinates = []
    names = []
    for feature in data['features']:
        coords = feature['geometry']['coordinates']
        name = feature['properties']['P11_001']  # 必要に応じて変更
        coordinates.append(coords)
        names.append(name)

    points = np.array(coordinates)
    triangulation = Delaunay(points)

    edges = []
    for simplex in triangulation.simplices:
        for i in range(3):
            for j in range(i + 1, 3):
                node1 = names[simplex[i]]
                node2 = names[simplex[j]]
                dist = np.linalg.norm(points[simplex[i]] - points[simplex[j]])
                edges.append((node1, node2, dist))

    # 距離を10～100に正規化
    normalized_edges = normalize_distances(edges, 10, 100)

    original_data = {
        "points": points,
        "names": names,
        "edges": normalized_edges
    }

    max_distance = max(d for _, _, d in normalized_edges)
    return create_graph_response(normalized_edges, points, names, centrality_type, max_distance)

@app.route("/filter_edges", methods=["POST"])
def filter_edges():
    global original_data

    threshold = float(request.form.get("threshold"))
    centrality_type = request.form.get("centrality", "degree")

    filtered_edges = [(u, v, d) for u, v, d in original_data["edges"] if d <= threshold]

    return create_graph_response(filtered_edges, original_data["points"], original_data["names"], centrality_type, threshold)

def create_graph_response(edges, points, names, centrality_type, max_distance):
    G = nx.Graph()

    for u, v, d in edges:
        G.add_edge(u, v, weight=d)

    if centrality_type == "degree":
        centralities = nx.degree_centrality(G)
    elif centrality_type == "closeness":
        centralities = nx.closeness_centrality(G, distance="weight")
    elif centrality_type == "betweenness":
        centralities = nx.betweenness_centrality(G)
    else:
        centralities = nx.degree_centrality(G)

    nodes = []
    for n in G.nodes():
        idx = names.index(n)
        nodes.append({
            "id": n,
            "centrality": float(centralities.get(n, 0)),
            "x": float(points[idx][0]),
            "y": float(points[idx][1]),
            "size": 8  # 固定サイズ8に設定
        })

    links = []
    for u, v in G.edges():
        data = G[u][v]
        links.append({
            "source": u,
            "target": v,
            "distance": float(data.get("weight", 0))
        })

    return jsonify({
        "nodes": nodes,
        "links": links,
        "max_distance": max(d for _, _, d in original_data["edges"])
    })

if __name__ == "__main__":
    app.run(debug=True)
