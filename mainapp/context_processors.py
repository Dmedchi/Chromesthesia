from basketapp.models import Basket
from mainapp.models import ProductCategory


def basket(request):
    # print(f'context processor basket works')
    basket = []
    if request.user.is_authenticated:
        basket = Basket.objects.filter(user=request.user)

    return {
        'basket': basket,
    }


def get_menu(request):
    # print(f'link_menu context_processor')
    menu = ProductCategory.objects.filter(is_active=True)

    return {
        'links_menu': menu,
    }
