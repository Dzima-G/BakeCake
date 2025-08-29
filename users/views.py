from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages

from .forms import SignupForm, LoginForm

User = get_user_model()


@require_POST
def register_user(request):
    form = SignupForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {'ok': False, 'message': 'Ошибка при регистрации.', 'errors': form.errors},
            status=400
        )
    user = User.objects.create_user(
        phone=form.cleaned_data['phone'],
        first_name=form.cleaned_data.get('first_name') or '',
        email=form.cleaned_data.get('email') or '',
        password=form.cleaned_data['password1'],
    )
    login(request, user)
    return JsonResponse({'ok': True, 'message': 'Вы успешно зарегистрировались!'}, status=200)


@require_POST
def login_view(request):
    form = LoginForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {'ok': False, 'message': 'Телефон или пароль неверны.', 'errors': form.errors},
            status=400
        )
    login(request, form.cleaned_data['user'])
    return JsonResponse({'ok': True, 'message': 'Вы успешно авторизованы!'}, status=200)


@login_required
def logout_view(request):
    logout(request)
    return redirect('storage:index')


@login_required
def profile_update(request):
    if request.method != 'POST':
        return redirect('storage:lk_user')

    user = request.user

    first_name = (request.POST.get('first_name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    phone = (request.POST.get('phone') or '').strip()
    password = request.POST.get('password') or ''

    updated = []

    if first_name and first_name != (user.first_name or ''):
        user.first_name = first_name
        updated.append('Имя')

    if email != (user.email or ''):
        user.email = email
        updated.append('Почта')

    if phone and phone != str(user.phone or ''):
        if User.objects.filter(phone=phone).exclude(pk=user.pk).exists():
            messages.error(request, 'Этот номер телефона уже зарегистрирован.')
            return redirect('storage:lk_user')
        user.phone = phone
        updated.append('Телефон')

    if password:
        user.set_password(password)
        updated.append('Пароль')

    if updated:
        user.save()
        if password:
            update_session_auth_hash(request, user)
        messages.success(request, f"Обновлены: {', '.join(updated)}.")

    return redirect('storage:lk_user')
