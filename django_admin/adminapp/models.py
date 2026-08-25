from django.db import models


class StoreUser(models.Model):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("staff", "Staff"),
        ("admin", "Admin"),
    )

    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "users"
        verbose_name = "store user"
        verbose_name_plural = "store users"

    def __str__(self):
        return self.email


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100)
    price = models.FloatField()
    popularity = models.FloatField(default=0)
    stock = models.IntegerField(default=0)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "products"
        ordering = ["-popularity", "name"]

    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(StoreUser, db_column="user_id", on_delete=models.DO_NOTHING, related_name="orders")
    total = models.FloatField()
    payment_status = models.CharField(max_length=30)
    order_status = models.CharField(max_length=30)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.pk}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, db_column="order_id", on_delete=models.DO_NOTHING, related_name="items")
    product = models.ForeignKey(Product, db_column="product_id", on_delete=models.DO_NOTHING)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.FloatField()

    class Meta:
        managed = False
        db_table = "order_items"


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, db_column="order_id", on_delete=models.DO_NOTHING, related_name="payments")
    amount = models.FloatField()
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=30)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "payments"
        ordering = ["-timestamp"]
