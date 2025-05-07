from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EarthquakeSearchForm, CustomUserCreationForm 
from datetime import datetime, timezone
import requests
from django.views.generic import TemplateView
from quakeapp.models import History
from datetime import datetime, timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



PREFECTURE_COORDINATES = {
    '北海道': {'minlat': 41.3, 'maxlat': 45.5, 'minlon': 139.3, 'maxlon': 145.8},
    '青森県': {'minlat': 40.3, 'maxlat': 41.5, 'minlon': 139.5, 'maxlon': 141.5},
    '岩手県': {'minlat': 38.8, 'maxlat': 40.5, 'minlon': 140.3, 'maxlon': 141.8},
    '宮城県': {'minlat': 37.8, 'maxlat': 39.2, 'minlon': 140.4, 'maxlon': 141.6},
    '秋田県': {'minlat': 39.2, 'maxlat': 40.5, 'minlon': 139.8, 'maxlon': 140.8},
    '山形県': {'minlat': 38.0, 'maxlat': 39.2, 'minlon': 139.5, 'maxlon': 140.5},
    '福島県': {'minlat': 36.8, 'maxlat': 38.2, 'minlon': 139.3, 'maxlon': 141.0},
    '茨城県': {'minlat': 35.7, 'maxlat': 36.9, 'minlon': 139.9, 'maxlon': 140.8},
    '栃木県': {'minlat': 36.2, 'maxlat': 37.0, 'minlon': 139.4, 'maxlon': 140.3},
    '群馬県': {'minlat': 36.1, 'maxlat': 37.0, 'minlon': 138.6, 'maxlon': 139.5},
    '埼玉県': {'minlat': 35.7, 'maxlat': 36.3, 'minlon': 138.9, 'maxlon': 139.9},
    '千葉県': {'minlat': 35.2, 'maxlat': 35.9, 'minlon': 139.7, 'maxlon': 140.9},
    '東京都': {'minlat': 35.5, 'maxlat': 35.8, 'minlon': 139.4, 'maxlon': 139.9},
    '神奈川県': {'minlat': 35.2, 'maxlat': 35.7, 'minlon': 139.2, 'maxlon': 139.8},
    '新潟県': {'minlat': 37.5, 'maxlat': 38.5, 'minlon': 138.2, 'maxlon': 139.6},
    '富山県': {'minlat': 36.5, 'maxlat': 37.0, 'minlon': 136.8, 'maxlon': 137.6},
    '石川県': {'minlat': 36.1, 'maxlat': 37.0, 'minlon': 136.4, 'maxlon': 137.5},
    '福井県': {'minlat': 35.6, 'maxlat': 36.3, 'minlon': 135.6, 'maxlon': 136.4},
    '山梨県': {'minlat': 35.2, 'maxlat': 35.9, 'minlon': 138.3, 'maxlon': 139.1},
    '長野県': {'minlat': 35.5, 'maxlat': 37.0, 'minlon': 137.5, 'maxlon': 139.0},
    '岐阜県': {'minlat': 35.2, 'maxlat': 36.6, 'minlon': 136.5, 'maxlon': 137.7},
    '静岡県': {'minlat': 34.6, 'maxlat': 35.4, 'minlon': 137.5, 'maxlon': 139.0},
    '愛知県': {'minlat': 34.8, 'maxlat': 35.4, 'minlon': 136.7, 'maxlon': 137.5},
    '三重県': {'minlat': 34.3, 'maxlat': 35.0, 'minlon': 136.0, 'maxlon': 137.2},
    '滋賀県': {'minlat': 35.0, 'maxlat': 35.6, 'minlon': 135.7, 'maxlon': 136.3},
    '京都府': {'minlat': 35.0, 'maxlat': 35.6, 'minlon': 135.3, 'maxlon': 136.1},
    '大阪府': {'minlat': 34.6, 'maxlat': 34.8, 'minlon': 135.4, 'maxlon': 135.6},
    '兵庫県': {'minlat': 34.6, 'maxlat': 35.5, 'minlon': 134.5, 'maxlon': 135.5},
    '奈良県': {'minlat': 34.3, 'maxlat': 34.6, 'minlon': 135.6, 'maxlon': 136.1},
    '和歌山県': {'minlat': 33.6, 'maxlat': 34.3, 'minlon': 135.2, 'maxlon': 135.9},
    '鳥取県': {'minlat': 35.2, 'maxlat': 35.6, 'minlon': 133.2, 'maxlon': 134.2},
    '島根県': {'minlat': 34.6, 'maxlat': 35.5, 'minlon': 132.4, 'maxlon': 133.3},
    '岡山県': {'minlat': 34.5, 'maxlat': 35.0, 'minlon': 133.5, 'maxlon': 134.0},
    '広島県': {'minlat': 34.2, 'maxlat': 34.8, 'minlon': 132.3, 'maxlon': 133.5},
    '山口県': {'minlat': 33.9, 'maxlat': 34.4, 'minlon': 130.8, 'maxlon': 132.3},
    '徳島県': {'minlat': 33.9, 'maxlat': 34.2, 'minlon': 133.6, 'maxlon': 134.6},
    '香川県': {'minlat': 34.1, 'maxlat': 34.4, 'minlon': 133.6, 'maxlon': 134.2},
    '愛媛県': {'minlat': 33.5, 'maxlat': 34.3, 'minlon': 132.5, 'maxlon': 133.8},
    '高知県': {'minlat': 32.7, 'maxlat': 33.6, 'minlon': 132.6, 'maxlon': 134.0},
    '福岡県': {'minlat': 33.3, 'maxlat': 33.9, 'minlon': 130.1, 'maxlon': 131.2},
    '佐賀県': {'minlat': 33.1, 'maxlat': 33.4, 'minlon': 129.8, 'maxlon': 130.3},
    '長崎県': {'minlat': 32.6, 'maxlat': 33.6, 'minlon': 128.6, 'maxlon': 130.0},
    '熊本県': {'minlat': 32.4, 'maxlat': 33.1, 'minlon': 130.2, 'maxlon': 131.1},
    '大分県': {'minlat': 32.8, 'maxlat': 33.5, 'minlon': 131.0, 'maxlon': 131.8},
    '宮崎県': {'minlat': 31.8, 'maxlat': 32.8, 'minlon': 131.0, 'maxlon': 131.6},
    '鹿児島県': {'minlat': 30.0, 'maxlat': 31.8, 'minlon': 129.2, 'maxlon': 131.0},
    '沖縄県': {'minlat': 24.0, 'maxlat': 26.8, 'minlon': 122.9, 'maxlon': 128.4},
    '全国': {'minlat': 20, 'maxlat': 46, 'minlon': 122, 'maxlon': 150},
}


# USGS APIから地震データを取得して地図に表示
@login_required
def earthquake_data_view(request):
    earthquakes = []
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'

    # GETリクエストからパラメータ取得
    year = request.GET.get('year', default=2000)   
    min_magnitude = safe_float(request.GET.get('min_magnitude'), default=3)
    max_magnitude = safe_float(request.GET.get('max_magnitude'), default=7)
    prefecture = request.GET.get('prefecture', '全国')
    
    # 都道府県から緯度経度を取得
    coords = PREFECTURE_COORDINATES.get(prefecture, {
        'minlat': 20,
        'maxlat': 46,
        'minlon': 122,
        'maxlon': 150
    })

    params = {
        'format': 'geojson',
        'limit': 1000,
        'minlatitude': coords['minlat'],
        'maxlatitude': coords['maxlat'],
        'minlongitude': coords['minlon'],
        'maxlongitude': coords['maxlon'],
        'orderby': 'time',
        'starttime': f'{year}-01-01',
        'endtime': f'{year}-12-31',
        'minmagnitude': float(min_magnitude),
        'maxmagnitude': float(max_magnitude),
    
    }
    
    #エラー処理
    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        earthquakes = []
        response = None

    if response.status_code == 200:
        data = response.json()
        for feature in data['features']:
            coords = feature['geometry']['coordinates']
            props = feature['properties']
            place = props['place'].replace("?", "o")
            earthquakes.append({
                'place': place,
                'magnitude': props['mag'],
                'time': datetime.fromtimestamp(props['time'] / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                'longitude': coords[0],
                'latitude': coords[1],
        })
            
    # --- 履歴をHistoryモデルに保存 ---
    if request.user.is_authenticated:
        user_searched = (
        str(request.GET.get('year')) != '2000' or
        str(request.GET.get('min_magnitude')) != '3' or
        str(request.GET.get('max_magnitude')) != '7' or
        request.GET.get('prefecture') not in [None, '', '全国']
        )
        if user_searched:
            year_int = safe_int(request.GET.get('year'), default=2000)
            History.objects.create(
                user=request.user,
                start_year=year_int,
                end_year=year_int,
                min_magnitude=min_magnitude,
                max_magnitude=max_magnitude,
                prefecture=prefecture
            )
    # --- ページネーション処理 ---
    page = request.GET.get('page', 1)
    paginator = Paginator(earthquakes, 10)  # 1ページ10件
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    all_earthquakes = earthquakes

    return render(request, 'quake/earthquake_data.html', {
        'all_earthquakes': all_earthquakes,  # 地図用に全データを渡す
        'page_obj': page_obj,  # テーブル用にページネーション済みデータ
        'year': year,
        'min_magnitude': min_magnitude,
        'max_magnitude': max_magnitude,
        'prefecture': prefecture,
    })

# マイページ（ログイン必須）
@login_required
def mypage_view(request):
    histories = History.objects.filter(user=request.user).order_by('-searched_at')
    return render(request, 'mypage.html', {'histories': histories})

YEAR_CHOICES = [(str(y), str(y)) for y in range(1900, 2101)]

# 検索ページ：DBから検索し履歴も保存
@login_required
def earthquake_search(request):
    form = EarthquakeSearchForm(request.GET or None)
    form.fields['year'].choices = YEAR_CHOICES
    earthquakes = []
    keyword = ''

    if form.is_valid():
        year = int(form.cleaned_data['year'])  # ← ここでint型に変換
        keyword = form.cleaned_data.get('keyword', '')
        earthquakes = EarthquakeData.objects.filter(
            location__icontains=keyword,
            date__year=year
        )
        # 履歴保存（GETパラメータ経由の検索のみ。履歴リンククリックは除く）
        if request.GET.get('from_history') != '1':
            History.objects.create(
                user=request.user,
                keyword=keyword,
                searched_at=datetime.now(timezone.utc)
            )

    return render(request, 'quake/earthquake_search.html', {
        'form': form,
        'earthquakes': earthquakes,
        'keyword': keyword,
    })

def safe_int(val, default=None):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default
    
def safe_float(val, default=None):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


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

class EarthquakeData(TemplateView):
    template_name = 'earthquake_data.html'
    # get_context_dataなどをオーバーライドして検索条件でデータ取得

def safe_int(val, default=None):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default








