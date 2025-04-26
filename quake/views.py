from django.shortcuts import render
import requests
from django.contrib.auth.decorators import login_required
from .forms import EarthquakeSearchForm
from .models import Earthquake
from datetime import datetime, timezone
import json  #地図表示不具合対応中の追加


# 直近の地震データをUSGS APIから取得・地図表示に使える形で渡す
def earthquake_data_view(request):
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
    params = {
        'format': 'geojson',
        'limit': 20,
        'minlatitude': 20,
        'maxlatitude': 46,
        'minlongitude': 122,
        'maxlongitude': 150,
        'orderby': 'time',
    }
    response = requests.get(url, params=params)

    earthquakes = []
    if response.status_code == 200:
        data = response.json()
        for feature in data['features']:
            coords = feature['geometry']['coordinates']
            props = feature['properties']
            earthquakes.append({
                'place': props['place'],
                'magnitude': props['mag'],
                'time': datetime.fromtimestamp(props['time'] / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                'longitude': coords[0],
                'latitude': coords[1],
            })
    else:
        earthquakes = []

    print(json.dumps(earthquakes, indent=2, ensure_ascii=False))  # ←確認用ログ

    return render(request, 'quake/earthquake_data.html', {'earthquakes': earthquakes})

# マイページ（ログインが必要）
@login_required
def mypage_view(request):
    return render(request, 'mypage.html')

# 地震検索ページ（年・マグニチュード・都道府県で絞り込み）
def earthquake_search(request):
    form = EarthquakeSearchForm(request.GET or None)
    results = None

    if form.is_valid():
        start_year = form.cleaned_data['start_year']
        end_year = form.cleaned_data['end_year']
        min_mag = form.cleaned_data['min_magnitude']
        max_mag = form.cleaned_data['max_magnitude']
        prefecture = form.cleaned_data['prefecture']

        results = Earthquake.objects.filter(
            date__year__gte=start_year,
            date__year__lte=end_year,
            magnitude__gte=min_mag,
            magnitude__lte=max_mag,
        )

        if prefecture:
            results = results.filter(location__icontains=prefecture)

    return render(request, 'quake/earthquake_search.html', {
        'form': form,
        'results': results,
    })

