from django.contrib import admin
from django.contrib import messages
from django.core.files.storage import default_storage
from django.db import connection, transaction

from .forms import OrderAdminForm, PaymentAdminForm, ProductAdminForm, StoreUserForm
from .models import Order, OrderItem, Payment, Product, StoreUser


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("name", "category", "price", "stock", "is_active", "popularity")
    list_filter = ("category", "is_active")
    search_fields = ("name", "category")
    list_editable = ("price", "stock", "is_active")

    def save_model(self, request, obj, form, change):
        uploaded_image = form.cleaned_data.get("image_upload")
        if uploaded_image:
            image_path = default_storage.save(
                f"products/{uploaded_image.name}", uploaded_image
            )
            obj.image_url = request.build_absolute_uri(
                f"/media/{image_path}"
            )
        super().save_model(request, obj, form, change)

    def _delete_unreferenced_products(self, request, product_ids):
        product_ids = list(product_ids)
        if not product_ids:
            return

        placeholders = ", ".join(["%s"] * len(product_ids))
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT product_id FROM order_items WHERE product_id IN ({placeholders}) "
                f"UNION SELECT product_id FROM cart_items WHERE product_id IN ({placeholders})",
                product_ids + product_ids,
            )
            referenced_ids = {row[0] for row in cursor.fetchall()}
            deletable_ids = [product_id for product_id in product_ids if product_id not in referenced_ids]
            if deletable_ids:
                delete_placeholders = ", ".join(["%s"] * len(deletable_ids))
                cursor.execute(
                    f"DELETE FROM products WHERE id IN ({delete_placeholders})",
                    deletable_ids,
                )

        if referenced_ids:
            self.message_user(
                request,
                "Referenced products were kept because they are used by carts or orders. "
                "Deactivate them instead of deleting them.",
                messages.WARNING,
            )

    def delete_model(self, request, obj):
        self._delete_unreferenced_products(request, [obj.pk])

    def delete_queryset(self, request, queryset):
        self._delete_unreferenced_products(request, queryset.values_list("pk", flat=True))


@admin.register(StoreUser)
class StoreUserAdmin(admin.ModelAdmin):
    form = StoreUserForm
    list_display = ("id", "email")
    list_filter = ("role", "is_active")
    search_fields = ("email", "role")
    readonly_fields = ("id",)

    def _delete_users_with_related_data(self, user_ids):
        user_ids = list(user_ids)
        if not user_ids:
            return

        placeholders = ", ".join(["%s"] * len(user_ids))
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM cart_items WHERE cart_id IN "
                    f"(SELECT id FROM carts WHERE user_id IN ({placeholders}))",
                    user_ids,
                )
                cursor.execute(
                    f"DELETE FROM carts WHERE user_id IN ({placeholders})",
                    user_ids,
                )
                cursor.execute(
                    f"DELETE FROM notifications WHERE user_id IN ({placeholders})",
                    user_ids,
                )
                cursor.execute(
                    f"DELETE FROM payments WHERE order_id IN "
                    f"(SELECT id FROM orders WHERE user_id IN ({placeholders}))",
                    user_ids,
                )
                cursor.execute(
                    f"DELETE FROM order_items WHERE order_id IN "
                    f"(SELECT id FROM orders WHERE user_id IN ({placeholders}))",
                    user_ids,
                )
                cursor.execute(
                    f"DELETE FROM orders WHERE user_id IN ({placeholders})",
                    user_ids,
                )
                cursor.execute(
                    f"DELETE FROM users WHERE id IN ({placeholders})",
                    user_ids,
                )

    def delete_model(self, request, obj):
        self._delete_users_with_related_data([obj.pk])

    def delete_queryset(self, request, queryset):
        self._delete_users_with_related_data(queryset.values_list("pk", flat=True))


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
    form = OrderAdminForm
    list_display = ("id", "user", "total", "payment_status", "order_status", "created_at")
    list_filter = ("payment_status", "order_status")
    search_fields = ("user__email",)
    readonly_fields = ("id", "created_at")
    inlines = (OrderItemInline, PaymentInline)

    def _delete_orders_with_related_data(self, order_ids):
        order_ids = list(order_ids)
        if not order_ids:
            return

        placeholders = ", ".join(["%s"] * len(order_ids))
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM payments WHERE order_id IN ({placeholders})",
                    order_ids,
                )
                cursor.execute(
                    f"DELETE FROM notifications WHERE order_id IN ({placeholders})",
                    order_ids,
                )
                cursor.execute(
                    f"DELETE FROM order_items WHERE order_id IN ({placeholders})",
                    order_ids,
                )
                cursor.execute(
                    f"DELETE FROM orders WHERE id IN ({placeholders})",
                    order_ids,
                )

    def delete_model(self, request, obj):
        self._delete_orders_with_related_data([obj.pk])

    def delete_queryset(self, request, queryset):
        self._delete_orders_with_related_data(queryset.values_list("pk", flat=True))


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = ("id", "order", "amount", "payment_method", "status", "timestamp")
    list_filter = ("payment_method", "status")
    search_fields = ("transaction_id",)
    readonly_fields = ("id",)
