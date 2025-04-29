from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EarthquakeSearchForm, CustomUserCreationForm
from .models import Earthquake, SearchHistory
from datetime import datetime, timezone
import requests

# USGS APIから地震データを取得して地図に表示
@login_required
def earthquake_data_view(request):
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'

    # GETリクエストからパラメータ取得
    start_year = request.GET.get('start_year', '2020')
    end_year = request.GET.get('end_year', '2025')
    min_magnitude = request.GET.get('min_magnitude', '4.1')
    max_magnitude = request.GET.get('max_magnitude', '10.2')
    prefecture = request.GET.get('prefecture', '')

    params = {
        'format': 'geojson',
        'limit': 20,
        'minlatitude': 20,
        'maxlatitude': 46,
        'minlongitude': 122,
        'maxlongitude': 150,
        'orderby': 'time',
        'starttime': f'{start_year}-01-01',
        'endtime': f'{end_year}-12-31',
        'minmagnitude': min_magnitude,
        'maxmagnitude': max_magnitude,
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

    if request.user.is_authenticated:
        keyword = f"{start_year}-{end_year}年, M{min_magnitude}-{max_magnitude}, {prefecture}"
        SearchHistory.objects.create(user=request.user, keyword=keyword)

    return render(request, 'quake/earthquake_data.html', {
        'earthquakes': earthquakes,
        'start_year': start_year,
        'end_year': end_year,
        'min_magnitude': min_magnitude,
        'max_magnitude': max_magnitude,
        'prefecture': prefecture,
    })


# マイページ（ログイン必須）
@login_required
def mypage_view(request):
    histories = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')
    return render(request, 'mypage.html', {'histories': histories})


# 検索ページ：DBから検索し履歴も保存
@login_required
def earthquake_search(request):
    form = EarthquakeSearchForm()
    return render(request, 'quake/earthquake_search.html', {'form': form})
    #form = EarthquakeSearchForm(request.GET or None)
    #results = None

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

        keyword = f"{start_year}-{end_year}年, M{min_mag}-{max_mag}, {prefecture}"
        SearchHistory.objects.create(user=request.user, keyword=keyword)

    return render(request, 'quake/earthquake_search.html', {
        'form': form,
        'results': results,
    })


# ログインページ
def login_view(request):
    return render(request, 'login.html')


# 新規登録ページ
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})








