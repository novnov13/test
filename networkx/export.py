import geojson
import networkx as nx
import numpy as np
from scipy.spatial import Delaunay
import csv
import os

# ファイルパスの指定（raw文字列リテラルまたはos.path.joinを使用）
file_path = r'C:\\data\\research\\gis_platform\\data\\bus.geojson'

# geojson ファイルを読み込む（utf-8-sigで開く）
with open(file_path, 'r', encoding='utf-8-sig') as f:
    data = geojson.load(f)

# 点の座標を抽出する
coordinates = []
names = []
for feature in data['features']:
    coords = feature['geometry']['coordinates']
    name = feature['properties']['P11_001']
    coordinates.append(coords)
    names.append(name)

# TIN（三角形分割）を生成する
points = np.array(coordinates)
triangulation = Delaunay(points)

# networkx のグラフを作成
G = nx.Graph()

# TIN の各三角形の辺を取り出し、グラフにエッジを追加する
for simplex in triangulation.simplices:
    # 三角形の3点（辺）を取り出す
    for i in range(3):
        for j in range(i + 1, 3):
            # ノード名をエッジとして追加
            node1 = names[simplex[i]]
            node2 = names[simplex[j]]
            # グラフにエッジ（距離）を追加
            dist = np.linalg.norm(points[simplex[i]] - points[simplex[j]])
            G.add_edge(node1, node2, weight=dist)

# CSV ファイルにエッジ情報を書き出す
with open('networkx_edges.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Node1', 'Node2', 'Distance'])
    for u, v, data in G.edges(data=True):
        writer.writerow([u, v, data['weight']])

print("CSVファイルを生成しました。")
