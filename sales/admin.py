from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "branch", "customer", "datetime", "payment_method", "total")
    list_filter = ("branch", "payment_method", "datetime")
    search_fields = ("id", "user__username", "customer__name")
    inlines = [SaleItemInline]

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("id", "sale", "item", "quantity", "price", "line_total")
    list_filter = ("item",)
    search_fields = ("item__name",)
