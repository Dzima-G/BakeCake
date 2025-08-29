from django import forms
from .models import Cake

class CakeForm(forms.ModelForm):
    class Meta:
        model = Cake
        fields = ['levels', 'form', 'topping', 'berries', 'decorations', 'text']