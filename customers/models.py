from django.db import models
from branches.models import Branch


class Customer(models.Model):
    CUSTOMER_TYPES = (
        ('regular', 'Regular'),
        ('vip', 'VIP'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=200)
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        db_index=True
    )
    address = models.TextField(blank=True, null=True)
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='regular'
    )
    branch = models.ForeignKey(
        Branch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_customer_type_display()})"

    class Meta:
        ordering = ['name']
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
