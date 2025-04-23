# quake/views.py
from django.shortcuts import render
import requests  # requestsをインポート

def earthquake_data_view(request):
    # USGS Earthquake APIから地震データを取得
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
    params = {'format': 'geojson', 'limit': 5}  # 直近の5つの地震データを取得
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()  # レスポンスをJSON形式で取得
    else:
        data = []  # APIリクエストが失敗した場合は空のリストをセット
    
    # 取得したデータをテンプレートに渡して表示
    return render(request, 'quake/earthquake_data.html', {'data': data})



