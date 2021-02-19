from django.contrib import admin
from django.urls import path, include
from .views import home,handler404,handler500


urlpatterns = [

    path('', home, name='home')
]
handler404 = handler404
handler500 = handler500
