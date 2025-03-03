from django.urls import path, include
from .views import *

urlpatterns = [
    path('api/', include('prizes_app.api.urls')),
    path('<prize_id>', prize_app_render),
]