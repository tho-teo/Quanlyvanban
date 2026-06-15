from django import forms
from .models import VanBanDen, VanBanDi

class VanBanDenForm(forms.ModelForm):
    class Meta:
        model = VanBanDen
        fields = '__all__'

class VanBanDiForm(forms.ModelForm):
    class Meta:
        model = VanBanDi
        fields = '__all__'
