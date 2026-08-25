from django import forms
from django.contrib.auth.models import User

from .models import Profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "bio"]

        widgets = {
            "avatar": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "maxlength": 160,
                }
            ),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")

        if avatar and avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Image must be 5 MB or smaller."
            )

        return avatar