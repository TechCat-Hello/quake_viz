# quake/urls.py
from django.urls import path
from . import views  # viewsをインポート
from .views import mypage_view

urlpatterns = [
    path('earthquake/', views.earthquake_data_view, name='earthquake_data'),
    path('mypage/', mypage_view, name='mypage'),
    path('search/', views.earthquake_search, name='earthquake_search'),

]







