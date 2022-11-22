from django.urls import path
from . import views

urlpatterns = [
    path('storages/', views.StorageList.as_view(), name="info"),
    path('quotes/', views.QuoteList.as_view()),
    path('quote/<int:pk>/', views.QuoteDetail.as_view()),
]