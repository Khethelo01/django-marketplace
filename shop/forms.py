"""Forms for the Marketplace application."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Store, Product, Review


class RegisterForm(UserCreationForm):
    """Registerform configuration and behaviour."""

    class Meta:
        """Configure model metadata or editable form fields."""

        model = User
        fields = ["username", "email", "role", "password1", "password2"]


class StoreForm(forms.ModelForm):
    """Storeform configuration and behaviour."""

    class Meta:
        """Configure model metadata or editable form fields."""

        model = Store
        fields = ["name", "description"]


class ProductForm(forms.ModelForm):
    """Productform configuration and behaviour."""

    class Meta:
        """Configure model metadata or editable form fields."""

        model = Product
        fields = ["name", "description", "price", "stock"]


class ReviewForm(forms.ModelForm):
    """Reviewform configuration and behaviour."""

    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={"min": 1, "max": 5, "step": 1}),
    )

    class Meta:
        """Configure model metadata or editable form fields."""

        model = Review
        fields = ["rating", "content"]
