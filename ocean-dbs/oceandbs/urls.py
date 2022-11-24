from django.urls import path
from . import views

urlpatterns = [
    path('storages/', views.StorageList.as_view(), name="info"),
    path('quote/<int:quoteId>/', views.QuoteStatus.as_view(), name="status"),
    path('quote/<int:quoteId>/link', views.QuoteLink.as_view(), name="link"),
    path('quotes/', views.QuoteList.as_view()),
    path('quote/<int:quoteId>/upload', views.UploadFile.as_view())
]