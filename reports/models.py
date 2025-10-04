from django.db import models
from sales.models import Sale
from inventory.models import Item
from branches.models import Branch


class DailySalesReport(models.Model):
    date = models.DateField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_orders = models.IntegerField(default=0)
    top_item = models.CharField(max_length=200, blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("date", "branch")

    def __str__(self):
        return f"Report {self.date} - {self.total_sales}"


class InventoryAlert(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="alerts")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    stock_level = models.IntegerField(default=0)  
    threshold = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.stock_level} left in {self.branch}"