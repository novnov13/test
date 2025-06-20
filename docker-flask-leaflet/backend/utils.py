def add_time(geojson):
    for index, feature in enumerate(geojson["features"]):
        feature["properties"]["time"] = str(2024 - index)

    return geojson
