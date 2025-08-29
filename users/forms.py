from django import forms
from django.contrib import auth
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()


class SignupForm(forms.Form):
    phone = PhoneNumberField(region='RU', label='Мобильный номер')
    first_name = forms.CharField(required=False, max_length=50, label='Имя')
    email = forms.EmailField(required=False, label='Почта')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')

    def clean(self):
        data = super().clean()
        if data.get('password1') != data.get('password2'):
            self.add_error('password2', 'Пароли не совпадают')

        phone = data.get('phone')
        if phone and User.objects.filter(phone=phone).exists():
            self.add_error('phone', 'Этот номер телефона уже зарегистрирован.')

        return data


class LoginForm(forms.Form):
    phone = PhoneNumberField(region='RU')
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        phone = data.get('phone')
        password = data.get('password')

        user = User.objects.filter(phone=phone).first()
        if not user or not user.check_password(password):
            raise forms.ValidationError('Не верный номер телефона или пароль.')

        data['user'] = user
        return data
