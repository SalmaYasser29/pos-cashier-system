from django.contrib import admin
from .models import Category, Item, Supplier, ActivityLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "branch")
    search_fields = ("name",)
    list_filter = ("branch",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sku", "price", "stock", "branch", "category")
    list_filter = ("branch", "category")
    search_fields = ("name", "sku")


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_person", "phone", "branch")
    search_fields = ("name", "contact_person", "phone")
    list_filter = ("branch",)


@admin.register(ActivityLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "model", "object_repr", "branch")
    list_filter = ("action", "model", "branch", "timestamp")
    search_fields = ("user__username", "object_repr", "model")
    date_hierarchy = "timestamp"

    # Make logs read-only
    readonly_fields = ("timestamp", "user", "action", "model", "object_id", "object_repr", "branch")

    def has_add_permission(self, request):
        return False  # Disable "Add" button

    def has_change_permission(self, request, obj=None):
        return False  # Disable editing

    def has_delete_permission(self, request, obj=None):
        return False  # Disable deletion
