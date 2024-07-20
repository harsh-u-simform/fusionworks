from django.contrib import admin
from django.urls import path
from .views import AskMe
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('/ask', csrf_exempt(AskMe.as_view()), name='ask'),
]
