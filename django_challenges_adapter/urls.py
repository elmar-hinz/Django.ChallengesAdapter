from django.urls import path, re_path

from . import views

app_name = "challenges"

urlpatterns = [
    path('', views.index),
    re_path(r'(?P<path>.*)', views.challenge)
]