from django.db import models
from django.conf import settings
from decimal import Decimal
from customers.models import Customer

class Sale(models.Model):
    ORDER_TYPES = [
        ('dine_in', 'Dine-in'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mixed', 'Mixed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default='takeaway')  
    table_number = models.CharField(max_length=10, null=True, blank=True)  
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')

    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))  # total before discount
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    final_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # total after discount
    cash_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    card_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey('inventory.Item', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
