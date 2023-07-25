from django.urls import path
from . import views

urlpatterns = [
    path('', views.StorageListView.as_view(), name="info"),
    path('register', views.StorageCreationView.as_view(), name="service-creation"),
    path('getStatus', views.QuoteStatusView.as_view(), name="status"),
    path('getLink', views.QuoteLink.as_view(), name="link"),
    path('getQuote', views.QuoteCreationView.as_view()),
    path('upload', views.UploadFile.as_view())
]