from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('quake/earthquake/')),  # ←これを追加
    path('quake/', include('quake.urls')),
]



