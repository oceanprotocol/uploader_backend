from django.urls import path
from . import views

urlpatterns = [
    path('storages/', views.StorageList.as_view(), name="info"),
    path('quote/<int:quoteId>/', views.QuoteStatus.as_view(), name="status"),
    path('quotes/', views.QuoteList.as_view()),
    path('upload/', views.UploadFile.as_view())
]