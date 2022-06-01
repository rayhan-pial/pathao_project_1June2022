from django import forms

from App_auth.models import Profile, CustomerShop
from App_main.models import *


class ProductModelForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = "__all__"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'shop']


class CustomerAddressForm(forms.ModelForm):
    class Meta:
        model = CustomerShop
        fields = "__all__"


class ProfilePictureChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "__all__"


class BillingForm(forms.ModelForm):
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'User country code like (+880)'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class': "selectpicker countrypicker"}))

    class Meta:
        model = BillingAddress
        fields = ['phone_number', 'shop_address', 'zip_code', 'city_zone', 'country']
