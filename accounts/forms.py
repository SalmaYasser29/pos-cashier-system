from django import forms
from .models import User

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["profile_image"]
