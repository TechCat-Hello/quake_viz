# quake/urls.py
from django.urls import path
from . import views  # viewsをインポート

urlpatterns = [
    path('earthquake/', views.earthquake_data_view, name='earthquake_data'),
]







