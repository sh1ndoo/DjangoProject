from django.urls import path, reverse_lazy
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='documents_list'),
    path('<int:document_id>', views.DocumentDetailView.as_view(), name='document_detail'),
]