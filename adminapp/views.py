from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse, reverse_lazy

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator

from adminapp.forms import ShopUserCreationAdminForm, ShopUserUpdateAdminForm, \
                           ProductCategoryEditForm, ProductEditForm
from authapp.models import ShopUser
from mainapp.models import ProductCategory, Product


class UsersListView(ListView):
    model = ShopUser
    template_name = 'adminapp/index.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'admin/users'
        return context


class CategoriesListView(ListView):
    model = ProductCategory
    template_name = 'adminapp/productcategory_list.html'

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'admin/categories'
        return context


class ProductsListView(ListView):
    model = Product
    template_name = 'adminapp/product_list.html'

    def get_queryset(self):
        pk = self.kwargs.get('pk')

        if int(pk) == 0 or int(pk) == 1:
            self.category = {
                'pk': 1,
                'name': 'все товары'
            }
            object_list = Product.objects.all().order_by('-is_active')
        else:
            self.category = get_object_or_404(ProductCategory, pk=pk)
            object_list = self.category.product_set.filter(category__pk=pk).order_by('-is_active')

        return object_list

    def get_context_data(self, **kwargs):
        context = super(ProductsListView, self).get_context_data(**kwargs)
        context['title'] = 'admin/products'
        context['category'] = self.category
        return context


class ShopuserCreateView(CreateView):
    model = ShopUser
    template_name = 'adminapp/shopuser_update.html'
    success_url = reverse_lazy('myadmin:index')
    form_class = ShopUserCreationAdminForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'users/create'
        return context


class ShopuserUpdateView(UpdateView):
    model = ShopUser
    template_name = 'adminapp/shopuser_update.html'
    success_url = reverse_lazy('myadmin:index')
    form_class = ShopUserUpdateAdminForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'users/update'
        return context


def shopuser_delete(request, pk):
    object = get_object_or_404(ShopUser, pk=pk)
    if request.method == 'POST':
        # object.delete()
        # вместо удаления лучше сделаем неактивным
        object.is_active = False
        object.save()
        return HttpResponseRedirect(reverse('myadmin:index'))

    content = {
        'title': 'users/delete',
        'user_to_delete': object
    }
    return render(request, 'adminapp/shopuser_delete.html', content)


class ProductCategoryCreateView(CreateView):
    model = ProductCategory
    template_name = 'adminapp/productcategory_update.html'
    success_url = reverse_lazy('myadmin:categories')
    # fields = '__all__'
    form_class = ProductCategoryEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'categories/create'
        return context


class ProductCategoryUpdateView(UpdateView):
    model = ProductCategory
    template_name = 'adminapp/productcategory_update.html'
    success_url = reverse_lazy('myadmin:categories')
    form_class = ProductCategoryEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'categories/update'
        return context


class ProductCategoryDeleteView(DeleteView):
    model = ProductCategory
    template_name = 'adminapp/productcategory_delete.html'
    success_url = reverse_lazy('myadmin:categories')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'categories/delete'
        return context


def product_create(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        form = ProductEditForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('myadmin:products', kwargs={'pk': pk}))
    else:
        form = ProductEditForm(initial={'category': category})

    content = {
        'title': 'products/create',
        'form': form,
        'category': category
    }
    return render(request, 'adminapp/product_update.html', content)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'adminapp/product_read.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'products/read'
        return context


def product_update(request, pk):
    product_object = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductEditForm(request.POST, request.FILES, instance=product_object)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('myadmin:products', kwargs={'pk': product_object.category.pk}))
    else:
        form = ProductEditForm(instance=product_object)

    content = {
        'title': 'products/update',
        'form': form,
        'category': product_object.category
    }
    return render(request, 'adminapp/product_update.html', content)


def product_delete(request, pk):
    object = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        object.is_active = False
        object.save()
        return HttpResponseRedirect(reverse('myadmin:products', kwargs={'pk': object.category.pk}))

    content = {
        'title': 'products/delete',
        'object': object,
        'category': object.category
    }
    return render(request, 'adminapp/product_delete.html', content)
