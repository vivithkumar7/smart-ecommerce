from django import forms
from passlib.context import CryptContext

from .models import StoreUser


password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class StoreUserForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Leave blank to keep the current password.",
    )

    class Meta:
        model = StoreUser
        fields = ("email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.password = password_context.hash(password)
        if commit:
            user.save(using=self._meta.model._default_manager.db)
        return user
