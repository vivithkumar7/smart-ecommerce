from django.contrib import admin

from .forms import StoreUserForm
from .models import Order, OrderItem, Payment, Product, StoreUser


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "popularity")
    list_filter = ("category", "is_active")
    search_fields = ("name", "category")
    list_editable = ("price", "stock", "is_active")


@admin.register(StoreUser)
class StoreUserAdmin(admin.ModelAdmin):
    form = StoreUserForm
    list_display = ("id", "email")
    search_fields = ("email",)
    readonly_fields = ("id",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "product_name", "quantity", "unit_price")


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    can_delete = False
    readonly_fields = ("amount", "payment_method", "transaction_id", "status", "timestamp")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total", "payment_status", "order_status", "created_at")
    list_filter = ("payment_status", "order_status")
    search_fields = ("user__email",)
    readonly_fields = ("id", "user", "total", "payment_status", "order_status", "created_at")
    inlines = (OrderItemInline, PaymentInline)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "amount", "payment_method", "status", "timestamp")
    list_filter = ("payment_method", "status")
    search_fields = ("transaction_id",)
    readonly_fields = tuple(field.name for field in Payment._meta.fields)
