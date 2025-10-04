from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "customer_type", "branch", "created_at")
    list_filter = ("customer_type", "branch", "created_at")
    search_fields = ("name", "phone", "email")
    ordering = ("name",)
    list_per_page = 25
