from django.db import models
from branches.models import Branch
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.timezone import now

User = get_user_model()

# -----------------------------
# Supplier
# -----------------------------
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'branch')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.branch.name if self.branch else 'No Branch'})"


# -----------------------------
# Category
# -----------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('name', 'branch')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


# -----------------------------
# Item
# -----------------------------
class Item(models.Model):
    sku = models.CharField(max_length=64, blank=True, null=True, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.PROTECT)  

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# -----------------------------
# Activity Log
# -----------------------------
class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("create", "Created"),
        ("update", "Updated"),
        ("delete", "Deleted"),
        ("view", "Viewed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model = models.CharField(max_length=50)  # e.g. "Category", "Item", "Supplier"
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(max_length=200)
    branch = models.ForeignKey(
        Branch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    old_data = models.TextField(null=True, blank=True)
    new_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.model} {self.object_repr} at {self.timestamp}"
