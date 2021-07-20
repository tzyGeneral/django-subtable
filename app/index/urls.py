from django.urls import path
from app.index import views

urlpatterns = [
    path('v1/test', views.TestView.as_view())
]