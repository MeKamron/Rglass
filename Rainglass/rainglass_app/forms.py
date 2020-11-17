from django import forms
from .models import *


class BuyurtmaForm(forms.ModelForm):
    class Meta:
        model = Buyurtma
        fields = ('picture',)

    def __init__(self, *args, **kwargs):
        super(BuyurtmaForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

