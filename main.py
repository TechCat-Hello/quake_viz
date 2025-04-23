import requests
import json

# USGS Earthquake APIからデータを取得
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
response = requests.get(url)

# 地震データを表示
data = response.json()
print(json.dumps(data, indent=4))
