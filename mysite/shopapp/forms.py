from decimal import Decimal

from django import forms
from django.core.validators import validate_image_file_extension

from shopapp.models import Product

MAX_IMAGE_SIZE_MB = 5


class MultipleFileInput(forms.ClearableFileInput):
    # Django 4.2+ требует явно разрешить выбор нескольких файлов
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """Поле для загрузки нескольких картинок. Каждая картинка валидируется отдельно."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            files = [single_clean(item, initial) for item in data if item]
        else:
            files = [single_clean(data, initial)] if data else []

        for image in files:
            validate_image_file_extension(image)
            if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(
                    f"Файл {image.name} больше {MAX_IMAGE_SIZE_MB} МБ."
                )
        return files


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = MultipleImageField(required=False)

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Название не может быть пустым.")
        return name

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price is None or price < Decimal("0"):
            raise forms.ValidationError("Цена не может быть отрицательной.")
        return price

    def clean_discount(self):
        discount = self.cleaned_data["discount"]
        if discount is None or not 0 <= discount <= 100:
            raise forms.ValidationError("Скидка должна быть от 0 до 100.")
        return discount


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.lower().endswith(".csv"):
            raise forms.ValidationError("Нужен файл с расширением .csv")
        return csv_file