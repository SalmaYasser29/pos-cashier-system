from django.contrib.auth.models import AbstractUser
from django.db import models

# ------------------------
# User model
# ------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    branch = models.ForeignKey('branches.Branch', null=True, blank=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='added_users'
    )
    profile_image = models.ImageField(upload_to="profiles/", null=True, blank=True)

    def __str__(self):
        return self.username

    @property
    def is_super_admin(self):
        """Check if user is superuser."""
        return self.is_superuser


# ------------------------
# Customer model
# ------------------------
class Customer(models.Model):
    TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('vip', 'VIP'),
    )
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    customer_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='regular')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.customer_type.upper()})"
