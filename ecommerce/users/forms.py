import logging
import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser

# Set up logging for this module
logger = logging.getLogger(__name__)

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        help_text="Enter your phone number (Canadian format)."
    )
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    verification_code = forms.CharField(max_length=4, required=True, label="4-Digit Code")

    # Additional optional fields
    company = forms.CharField(max_length=255, required=False)
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Your birthday! You'll get a gift or discount on your birthday."
    )
    country = forms.CharField(max_length=100, required=False)
    address = forms.CharField(max_length=255, required=False)
    address2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    province = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, required=True)

    class Meta:
        model = CustomUser
        fields = (
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "company",
            "birth_date",
            "country",
            "address",
            "address2",
            "city",
            "province",
            "postal_code",
            'verification_code'
        )

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) != 10:
            raise forms.ValidationError("Please enter a valid 10-digit Canadian phone number.")
        logger.debug("Cleaned phone number: %s", digits_only)
        return digits_only

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            logger.warning("Passwords do not match.")
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "company",
            "birth_date",
            "country",
            "address",
            "address2",
            "city",
            "province",
            "postal_code",

        )





from django import forms
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_image']

