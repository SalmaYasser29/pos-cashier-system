from django.contrib import admin
from .models import InventoryAlert, DailySalesReport

@admin.register(InventoryAlert)
class InventoryAlertAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "stock_level", "threshold", "created_at")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

@admin.register(DailySalesReport)
class DailySalesReportAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "total_sales", "total_orders", "top_item", "generated_at")
    ordering = ("-date",)
