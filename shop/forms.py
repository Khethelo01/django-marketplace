from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Store, Product, Review


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "description"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "content"]
