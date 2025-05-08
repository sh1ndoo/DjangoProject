from django.shortcuts import render
from django.views.generic import ListView, DetailView

from documents_app.models import Document
from events_app.utils import GlobalContextMixin


class DocumentListView(GlobalContextMixin, ListView):
    model = Document
    template_name = 'documents_app/documents_list.html'
    context_object_name = 'documents'


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents_app/document_detail.html'
    # slug_field = 'name'
    pk_url_kwarg = 'document_id'
    context_object_name = 'document'
