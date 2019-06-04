import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from mainapp.models import ProductCategory, Product

columns = [
    {
        'title': 'Our Account',
        'href1': 'Your Account',
        'href2': 'Personal information',
        'href3': 'Addresses',
        'href4': 'Discount',
        'href5': 'Orders history',
        'href6': 'Search Terms'
    },
    {
        'title': 'Our Support',
        'href1': 'Site Map',
        'href2': 'Search Terms',
        'href3': 'Advanced Search',
        'href4': 'Mobile',
        'href5': 'Contact Us',
        'href6': 'Addresses'
    },
]


def get_hot_product():
    return random.choice(Product.objects.filter(is_active=True))


def get_same_product(hot_product):
    return hot_product.category.product_set.filter(is_active=True).exclude(pk=hot_product.pk)[:3]


def index(request):
    content = {
        'title': 'Home',
        'columns': columns,
    }
    return render(request, 'mainapp/index.html', content)


def category(request, pk, page=1):
    if int(pk) == 0 or int(pk) == 1:
        category = {
            'pk': 1,
            'name': 'все товары',
        }
        products = Product.objects.filter(is_active=True, category__is_active=True).order_by('price')
    else:
        category = get_object_or_404(ProductCategory, pk=pk)
        products = category.product_set.filter(category__pk=pk, is_active=True, category__is_active=True).order_by('price')

    paginator = Paginator(products, 2)
    try:
        products_paginator = paginator.page(page)
    except PageNotAnInteger:
        products_paginator = paginator.page(1)
    except EmptyPage:
        products_paginator = paginator.page(paginator.num_pages)

    content = {
        'title': 'Products',
        'category': category,
        'products': products_paginator,
        'columns': columns,
    }
    return render(request, 'mainapp/products_list.html', content)


def products(request):
    hot_product = get_hot_product()
    same_products = get_same_product(hot_product)

    content = {
        'title': 'Products',
        'hot_product': hot_product,
        'same_products': same_products,
        'columns': columns,
    }
    return render(request, 'mainapp/products.html', content)


def product(request, pk):
    content = {
        'title': 'Product',
        'object': get_object_or_404(Product, pk=pk),
        'columns': columns,
    }
    return render(request, 'mainapp/product.html', content)


def contacts(request):
    content = {
        'title': 'Contacts',
        'columns': columns,
    }
    return render(request, 'mainapp/contacts.html', content)
