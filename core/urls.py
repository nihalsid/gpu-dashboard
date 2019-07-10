from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('user_distribution', views.get_user_distribution, name='usage'),
    path('usage_history', views.get_usage_history, name='timeline'),
]
