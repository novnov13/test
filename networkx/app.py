from flask import Flask, render_template, request, jsonify
import networkx as nx
import pandas as pd
import json

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    centrality_type = request.form.get("centrality", "degree")

    df = pd.read_csv(file)
    df['distance'] = df['distance'].astype(float)
    # 'distance'があれば、それをエッジの重みとして使用
    G = nx.from_pandas_edgelist(df, source='node1', target='node2', edge_attr='distance')

    # 中心性を計算
    centralities = {
        "degree": nx.degree_centrality(G),
        "closeness": nx.closeness_centrality(G, distance='distance')
    }

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
            {
                "source": str(u),
                "target": str(v),
                "distance": G[u][v].get("distance", 0)  # 重み (distance)
            }
            for u, v in G.edges()
        ]
    }

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
