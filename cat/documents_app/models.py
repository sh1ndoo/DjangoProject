from django.db import models

class Document(models.Model):
    class Meta:
        verbose_name_plural = 'Документы'
        verbose_name = 'Документ'

    text = models.TextField(verbose_name='Документ')
    name = models.CharField(max_length=100, verbose_name='Название документа')
