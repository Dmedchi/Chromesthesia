from django.core.management.base import BaseCommand
from mainapp.models import ProductCategory, Product
from authapp.models import ShopUser

import json
import os

JSON_PATH = 'mainapp/json'


def load_from_json(file_name):
    with open(os.path.join(JSON_PATH, file_name + '.json'), 'r', encoding='utf-8') as infile:
        return json.load(infile)


class Command (BaseCommand):
    def handle(self, *args, **options):
        categories = load_from_json('categories')
        ProductCategory.objects.all().delete()
        for category in categories:
            ProductCategory.objects.create(**category)

        products = load_from_json('products')
        Product.objects.all().delete()
        for product in products:
            category_name = product['category']
            # Получаем категорию по имени
            _category = ProductCategory.objects.filter(name=category_name).first()
            # Заменяем название категории объектом
            product['category'] = _category
            Product.objects.create(**product)

        # Проверяем наличие суперпользователя, если нет, то создаем
        if not ShopUser.objects.filter(username='django').exists():
            ShopUser.objects.create_superuser('django', 'django@geekshop.local', 'geekbrains', age=25)
