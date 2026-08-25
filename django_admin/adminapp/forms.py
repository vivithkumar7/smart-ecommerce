from django import forms
from passlib.context import CryptContext

from django.utils import timezone

from .models import Order, Payment, Product, StoreUser


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
        fields = ("email", "password", "role", "is_active")

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.password = password_context.hash(password)
        if commit:
            user.save(using=self._meta.model._default_manager.db)
        return user


class ProductAdminForm(forms.ModelForm):
    image_upload = forms.ImageField(required=False, label="Upload product image")

    class Meta:
        model = Product
        fields = "__all__"


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("user", "total", "payment_status", "order_status")


class PaymentAdminForm(forms.ModelForm):
    timestamp = forms.DateTimeField(initial=timezone.now)

    class Meta:
        model = Payment
        fields = ("order", "amount", "payment_method", "transaction_id", "status", "timestamp")
