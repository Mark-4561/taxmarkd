from django.urls import path, include
from tax import views

urlpatterns = [
    path('ORCImg', views.ORCImg.as_view()),
]
