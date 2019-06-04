from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from authapp.models import ShopUser
from django.db import transaction
from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm, \
                          ShopUserEditForm, ShopUserProfileEditForm


def login(request):
    next = request.GET['next'] if 'next' in request.GET.keys() else ''

    if request.method == 'POST':
        form = ShopUserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user)
                if 'next' in request.POST.keys():
                    return HttpResponseRedirect(request.POST['next'])
                else:
                    return HttpResponseRedirect(reverse('main:index'))
    else:
        form = ShopUserLoginForm()

    content = {
        'title': 'Вход',
        'form': form,
        'next': next
    }
    return render(request, 'authapp/login.html', content)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main:index'))


def register(request):
    if request.method == 'POST':
        form = ShopUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if send_verify_mail(user):
                print('Сообщение для подтверждения регистрации отправлено')
                # return HttpResponseRedirect(reverse('auth:login'))
                return render(request, 'authapp/confirm.html')
            else:
                print('ошибка отправки сообщения')
                return HttpResponseRedirect(reverse('auth:login'))
    else:
        form = ShopUserRegisterForm()

    content = {
        'title': 'Регистрация',
        'form': form
    }
    return render(request, 'authapp/register.html', content)


@transaction.atomic
def update(request):
    if request.method == 'POST':
        form = ShopUserEditForm(request.POST, request.FILES,
                                instance=request.user)
        profile_form = ShopUserProfileEditForm(request.POST, instance=request.user.shopuserprofile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('auth:update'))
    else:
        form = ShopUserEditForm(instance=request.user)
        profile_form = ShopUserProfileEditForm(instance=request.user.shopuserprofile)

    content = {
        'title': 'Редактирование',
        'form': form,
        'profile_form': profile_form
    }
    return render(request, 'authapp/update.html', content)


def send_verify_mail(user):
    verify_link = reverse('auth:verify',
                          args=[user.email, user.activation_key])

    title = 'Подтверждение учетной записи {}'.format(user.username)

    message = 'Для подтверждения учетной записи {} на портале {} перейдите по ссылке: \n{}{}'.format(user.username,
                                                                                                     settings.DOMAIN_NAME,
                                                                                                     settings.DOMAIN_NAME,
                                                                                                     verify_link)

    print('from: {} to: {}'.format(settings.EMAIL_HOST_USER, user.email))
    return send_mail(title,
                     message,
                     settings.EMAIL_HOST_USER,
                     [user.email],
                     fail_silently=False)


def verify(request, email, activation_key):
    try:
        user = ShopUser.objects.get(email=email)
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            auth.login(request, user,
                       backend='django.contrib.auth.backends.ModelBackend')
            return render(request, 'authapp/verification.html')
        else:
            print('error activation user: {}'.format(user))
            return render(request, 'authapp/verification.html')
    except Exception as e:
        print('error activation user: {}'.format(e.args))
        return HttpResponseRedirect(reverse('main:index'))
