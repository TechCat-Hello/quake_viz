# quake/urls.py
from django.urls import path
from . import views  # viewsをインポート
from .views import mypage_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('earthquake/', views.earthquake_data_view, name='earthquake_data'),
    path('mypage/', mypage_view, name='mypage'),
    path('search/', views.earthquake_search, name='earthquake_search'),
    path('login/', views.login_view, name='login'),
    #path('login/', auth_views.LoginView.as_view(), name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('data/', views.earthquake_data_view, name='earthquake_data'),
    path('history/delete/<int:history_id>/', views.delete_history, name='delete_history'),

]







