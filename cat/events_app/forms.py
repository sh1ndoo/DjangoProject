# events/forms.py
from django import forms
from django.utils import timezone
from taggit.forms import TagWidget # Import TagWidget for better tag input styling
from .models import Events, Categories, Locations # Import your models
import re # Импортируем модуль для работы с регулярными выражениями





class EventCreateForm(forms.ModelForm):
    """
    Form for creating new Events based on the Events model.
    """
    cat = forms.ModelChoiceField(
        queryset=Categories.objects.all(),
        widget=forms.Select(attrs={
                'class': 'form-control'
            }),
        empty_label='Выберите категорию...')

    loc = forms.ModelChoiceField(
        queryset=Locations.objects.all(),
        widget=forms.Select(attrs={
                'class': 'form-control',
            }),
        empty_label='Выберите город...',
        required=False
    )
    address = forms.CharField(
        widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адрес места',
                'id': 'selected-address',
                'readonly': 'readonly'
            }),
        label='Адрес места',

    )
    address_name = forms.CharField(
        widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название места',
                'id': 'selected-name'
            }),
        label='Название места'
    )

    address_description = forms.CharField(
        widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Короткий адрес',
                'id': 'selected-description',
                'readonly': 'readonly'
            }),
        label='Короткий адрес'
    )

    address_city = forms.CharField(
        widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Город',
                'id': 'selected-city',
            }),
        required=True,
        label='Город'
    )

    class Meta:
        model = Events

        fields = [
            'name', 'anons', 'cat', 'loc', 'tags',
            'date_start', 'date_end',
            'is_free', 'min_price', 'max_price', 'age', 'logo'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название мероприятия'
            }),
            'anons': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Краткое описание или анонс события...'
            }),
            'cat': forms.Select(attrs={
                'class': 'form-control'
            }),
            'loc': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': TagWidget(attrs={
                 'class': 'form-control',
                 'placeholder': 'Введите теги через запятую'
            }),
            'date_start': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'date_end': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'is_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'min_price': forms.NumberInput(attrs={
                'class': 'form-control price-input', # Class for JS
                'placeholder': '0',
                'min': '0',
                'step': '10',
                'size': '2'
            }),
            'max_price': forms.NumberInput(attrs={
                'class': 'form-control price-input', # Class for JS
                'placeholder': '0',
                'min': '0',
                'step': '10',
                'size': '2'
            }),
            'age': forms.TextInput(attrs={
                'class': 'form-control age-input',
                'placeholder': '0+',
                'size': '3',
                'align': 'center',
                'pattern': r'\d{1,2}\+',
                'title': 'Введите возраст в формате "00+", например "6+" или "18+"'
            }),
            'logo': forms.FileInput(attrs={
                'hidden': True,
                'id': 'logo'
            }),
        }

        labels = {
            'name': 'Название события',
            'anons': 'Анонс/Описание',
            'cat': 'Категория',
            'loc': 'Локация',
            'date_start': 'Дата и время начала',
            'date_end': 'Дата и время окончания',
            'is_free': 'Бесплатно',
            'min_price': 'Мин. цена (руб)',
            'max_price': 'Макс. цена (руб)',
            'age': 'Возраст. ограничение',
            'logo': 'URL основного логотипа',
            'address': 'Адрес места',
            'address_name': 'Название места'
        }

    def __init__(self, *args, **kwargs):
        """Устанавливаем required атрибут на основе модели."""
        super().__init__(*args, **kwargs)

    def clean_age(self):
        """
        Валидирует поле 'age', проверяя формат "ЧЧ+".
        """
        # Получаем значение поля из cleaned_data
        age_value = self.cleaned_data.get('age')

        # Если поле не обязательное и оно пустое, то валидация пройдена
        # Убедитесь, что required=False для поля age в модели или форме, если пустое значение допустимо
        if not age_value:
            return age_value  # Возвращаем пустое значение (None или '')

        # Регулярное выражение для формата "одна-две цифры плюс"
        age_regex = r'^\d{1,2}\+$'

        # Проверяем соответствие строки регулярному выражению
        if not re.fullmatch(age_regex, age_value):
            # Если не соответствует, вызываем ValidationError
            raise forms.ValidationError(
                'Возрастное ограничение должно быть в формате "ЧЧ+" (например, "6+" или "18+").',
                code='invalid_age_format'  # Уникальный код ошибки (опционально)
            )

        # Если валидация пройдена, возвращаем очищенное значение
        return age_value


    def clean_date_end(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')

        if date_start and date_end and date_end < date_start:
            self.add_error('date_end',"Дата окончания не может быть раньше даты начала.")
        return date_end

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if is_free:
            if min_price is not None and min_price > 0:
                self.add_error('min_price', 'Для бесплатных событий цена должна быть 0.')
            if max_price is not None and max_price > 0:
                self.add_error('max_price', 'Для бесплатных событий цена должна быть 0.')

            cleaned_data['min_price'] = 0
            cleaned_data['max_price'] = 0
        else:
            if min_price is None:
                 self.add_error('min_price', 'Укажите минимальную цену или отметьте "Бесплатно".')
            elif min_price < 0:
                 self.add_error('min_price', 'Минимальная цена не может быть отрицательной.')

            if max_price is None:
                 self.add_error('max_price', 'Укажите максимальную цену или отметьте "Бесплатно".')
            elif max_price < 0:
                 self.add_error('max_price', 'Максимальная цена не может быть отрицательной.')

        return cleaned_data