# views.py

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, ProtectedError
from django.template.loader import render_to_string
from collections import OrderedDict
import json, ast

from .models import Category, Item, Supplier, ActivityLog
from .forms import CategoryForm, ItemForm, SupplierForm
from .utils import log_action, get_changes


# -----------------------------
# Role Helpers
# -----------------------------
def is_superuser(user):
    return user.is_superuser


def is_admin(user):
    return getattr(user, "role", "") == "admin"


# -----------------------------
# Dashboard
# -----------------------------
@login_required
def index(request):
    if is_superuser(request.user):
        categories = Category.objects.all()
        items = Item.objects.all().select_related("category", "branch", "supplier")
        suppliers = Supplier.objects.all()
    elif is_admin(request.user):
        branch = getattr(request.user, "branch", None)
        categories = Category.objects.filter(branch=branch)
        items = Item.objects.filter(branch=branch).select_related("category", "branch", "supplier")
        suppliers = Supplier.objects.filter(branch=branch)
    else:
        return redirect("accounts:dashboard")

    return render(request, "inventory/index.html", {
        "categories": categories,
        "items": items,
        "suppliers": suppliers,
    })


# -----------------------------
# Category Views
# -----------------------------
@login_required
def category_list(request):
    query = request.GET.get("q", "")

    if is_superuser(request.user):
        categories = Category.objects.select_related("branch").all()
    elif is_admin(request.user):
        categories = Category.objects.filter(branch=request.user.branch).select_related("branch")
    else:
        return redirect("accounts:dashboard")

    if query:
        categories = categories.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(branch__name__icontains=query)
        )

    categories = categories.order_by("branch__name", "name")

    # Paginate per branch
    branches = OrderedDict()
    for branch in categories.values_list("branch", flat=True).distinct():
        branch_cats = categories.filter(branch=branch)
        page_number = request.GET.get(f"page_{branch}", 1)
        paginator = Paginator(branch_cats, 10)
        page_obj = paginator.get_page(page_number)
        branches[branch_cats.first().branch] = page_obj

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("inventory/categories/_categories_table.html", {
            "branches": branches,
            "query": query,
            "user": request.user,
        }, request=request)
        return JsonResponse({"html": html})

    return render(request, "inventory/categories/list.html", {
        "branches": branches,
        "query": query,
    })


@login_required
def category_create(request):
    if not (is_superuser(request.user) or is_admin(request.user)):
        return redirect("inventory:category_list")

    if request.method == "POST":
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            if not is_superuser(request.user):
                category.branch = request.user.branch
            category.save()
            log_action(request.user, "create", category)
            messages.success(request, f"Category '{category.name}' created.")
            return redirect("inventory:category_list")
    else:
        form = CategoryForm(user=request.user)

    return render(request, "inventory/categories/form.html", {"form": form})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if not (is_superuser(request.user) or (is_admin(request.user) and category.branch == request.user.branch)):
        return redirect("inventory:category_list")

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category, user=request.user)
        if form.is_valid():
            old_instance = Category.objects.get(pk=category.pk)  # snapshot before save
            category = form.save(commit=False)
            if not is_superuser(request.user):
                category.branch = request.user.branch
            category.save()
            log_action(request.user, "update", category, old_instance)
            messages.success(request, f"Category '{category.name}' updated.")
            return redirect("inventory:category_list")
    else:
        form = CategoryForm(instance=category, user=request.user)

    return render(request, "inventory/categories/form.html", {"form": form})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    # Permission check
    if not (is_superuser(request.user) or (is_admin(request.user) and category.branch == request.user.branch)):
        return redirect("inventory:category_list")

    if request.method == "POST":
        if category.item_set.exists():
            return render(request, "inventory/categories/cannot_delete.html", {
                "category": category,
                "items": category.item_set.all()
            })

        try:
            old_instance = Category.objects.get(pk=category.pk)  
            name = category.name
            category.delete()
            log_action(request.user, "delete", old_instance)
            messages.success(request, f"Category '{name}' deleted.")
            return redirect("inventory:category_list")
        except ProtectedError as e:
            protected_objects = list(e.protected_objects)
            return render(request, "inventory/categories/confirm_delete.html", {
                "category": category,
                "error": f"Cannot delete '{category.name}' because it is referenced by: "
                         f"{', '.join(str(obj) for obj in protected_objects)}"
            })

    return render(request, "inventory/categories/confirm_delete.html", {"category": category})


# -----------------------------
# Item Views
# -----------------------------
@login_required
def item_list(request):
    query = request.GET.get("q", "")

    # Get items depending on user role
    if is_superuser(request.user):
        items = Item.objects.select_related("category", "branch", "supplier").all()
    elif is_admin(request.user):
        items = Item.objects.filter(branch=request.user.branch).select_related("category", "branch", "supplier")
    else:
        return redirect("accounts:dashboard")

    # Apply search filter
    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(branch__name__icontains=query) |
            Q(supplier__name__icontains=query)
        )

    # No paginator here → you want *all items grouped per branch*
    items = items.order_by("branch__name", "category__name", "name")

    # Regroup data in Python to avoid template complexity
    from itertools import groupby
    from operator import attrgetter

    grouped_items = []
    for branch, branch_items in groupby(items, key=attrgetter("branch")):
        grouped_items.append((branch, list(branch_items)))

    # AJAX response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string("_items_table.html", {
            "grouped_items": grouped_items,
            "user": request.user,
        }, request=request)
        return JsonResponse({"html": html})

    return render(request, "inventory/items/list.html", {
        "grouped_items": grouped_items,
        "query": query,
    })


@login_required
def item_create(request):
    if not (is_superuser(request.user) or is_admin(request.user)):
        return redirect("inventory:item_list")

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            if not is_superuser(request.user):
                item.branch = request.user.branch
            item.save()
            log_action(request.user, "create", item)
            messages.success(request, f"Item '{item.name}' created.")
            return redirect("inventory:item_list")
    else:
        form = ItemForm(user=request.user)

    return render(request, "inventory/items/form.html", {"form": form})


@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if not (is_superuser(request.user) or (is_admin(request.user) and item.branch == request.user.branch)):
        return redirect("inventory:item_list")

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item, user=request.user)
        if form.is_valid():
            old_instance = Item.objects.get(pk=item.pk)  # snapshot before save
            item = form.save(commit=False)
            if not is_superuser(request.user):
                item.branch = request.user.branch
            item.save()
            log_action(request.user, "update", item, old_instance)
            messages.success(request, f"Item '{item.name}' updated.")
            return redirect("inventory:item_list")
    else:
        form = ItemForm(instance=item, user=request.user)

    return render(request, "inventory/items/form.html", {"form": form})


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)

    # Permission check
    if not (is_superuser(request.user) or (is_admin(request.user) and item.branch == request.user.branch)):
        return redirect("inventory:item_list")

    # Check if this item is linked to any sales
    linked_sales = item.saleitem_set.all()  # <-- correct reverse relation

    if request.method == "POST":
        if linked_sales.exists():
            # Build a list of linked sales for display
            reason = [f"Sale #{si.sale.id} ({si.sale.datetime.strftime('%Y-%m-%d %H:%M')}) x {si.quantity}" 
                      for si in linked_sales]
            return render(request, "inventory/items/cannot_delete.html", {
                "item": item,
                "reason": reason
            })
        else:
            # Safe to delete
            old_instance = Item.objects.get(pk=item.pk)
            name = item.name
            item.delete()
            log_action(request.user, "delete", old_instance)
            messages.success(request, f"Item '{name}' deleted successfully.")
            return redirect("inventory:item_list")

    return render(request, "inventory/items/confirm_delete.html", {"item": item})


@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if not (is_superuser(request.user) or (is_admin(request.user) and item.branch == request.user.branch)):
        return redirect("inventory:item_list")
    return render(request, "inventory/items/detail.html", {"item": item})


@login_required
def search_items(request):
    q = request.GET.get("q", "")
    if is_superuser(request.user):
        qs = Item.objects.filter(name__icontains=q)[:30]
    elif is_admin(request.user):
        qs = Item.objects.filter(branch=request.user.branch, name__icontains=q)[:30]
    else:
        qs = Item.objects.none()

    data = [
        {
            "id": i.id,
            "name": i.name,
            "price": str(i.price),
            "stock": i.stock,
            "category": i.category.name if i.category else None,
            "branch": i.branch.name if i.branch else None,
            "supplier": i.supplier.name if i.supplier else None
        }
        for i in qs
    ]
    return JsonResponse({"items": data})


# -----------------------------
# Supplier Views
# -----------------------------
@login_required
def supplier_list(request):
    query = request.GET.get("q", "")
    page_number = request.GET.get("page", 1)

    if is_superuser(request.user):
        suppliers = Supplier.objects.all()
    elif is_admin(request.user):
        suppliers = Supplier.objects.filter(branch=request.user.branch)
    else:
        return redirect("accounts:dashboard")

    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) |
            Q(contact_person__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(suppliers.order_by("name"), 10)
    page_obj = paginator.get_page(page_number)

    return render(request, "inventory/suppliers/list.html", {
        "suppliers": page_obj,
        "query": query,
    })


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if not (is_superuser(request.user) or (is_admin(request.user) and supplier.branch == request.user.branch)):
        return redirect("inventory:supplier_list")
    return render(request, "inventory/suppliers/detail.html", {"supplier": supplier})


@login_required
def supplier_create(request):
    if not (is_superuser(request.user) or is_admin(request.user)):
        return redirect("inventory:supplier_list")

    if request.method == "POST":
        form = SupplierForm(request.POST, user=request.user)
        if form.is_valid():
            supplier = form.save(commit=False)
            if not is_superuser(request.user):
                supplier.branch = request.user.branch
            supplier.save()
            log_action(request.user, "create", supplier)
            messages.success(request, f"Supplier '{supplier.name}' created.")
            return redirect("inventory:supplier_list")
    else:
        form = SupplierForm(user=request.user)

    return render(request, "inventory/suppliers/form.html", {"form": form})


@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if not (is_superuser(request.user) or (is_admin(request.user) and supplier.branch == request.user.branch)):
        return redirect("inventory:supplier_list")

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier, user=request.user)
        if form.is_valid():
            old_instance = Supplier.objects.get(pk=supplier.pk)  # snapshot before save
            supplier = form.save(commit=False)
            if not is_superuser(request.user):
                supplier.branch = request.user.branch
            supplier.save()
            log_action(request.user, "update", supplier, old_instance)
            messages.success(request, f"Supplier '{supplier.name}' updated.")
            return redirect("inventory:supplier_list")
    else:
        form = SupplierForm(instance=supplier, user=request.user)

    return render(request, "inventory/suppliers/form.html", {"form": form})


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    
    # Permission check
    if not (is_superuser(request.user) or (is_admin(request.user) and supplier.branch == request.user.branch)):
        return redirect("inventory:supplier_list")

    # Handle POST
    if request.method == "POST":
        try:
            old_instance = Supplier.objects.get(pk=supplier.pk)  # snapshot
            name = supplier.name
            supplier.delete()
            log_action(request.user, "delete", old_instance)
            messages.success(request, f"Supplier '{name}' deleted.")
            return redirect("inventory:supplier_list")
        except ProtectedError as e:
            protected_objects = list(e.protected_objects)
            # Redirect to cannot_delete.html
            return render(request, "inventory/suppliers/cannot_delete.html", {
                "supplier": supplier,
                "reason": [str(obj) for obj in protected_objects]
            })

    # Render confirm delete
    return render(request, "inventory/suppliers/confirm_delete.html", {"supplier": supplier})


# -----------------------------
# Logs
# -----------------------------
def safe_load(data):
    if not data:
        return {}
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(data)
        except Exception:
            return {}


@login_required
def logs_list(request, model, object_id):
    logs = ActivityLog.objects.filter(
        model=model, object_id=object_id
    ).order_by("-timestamp")

    for log in logs:
        if log.action == "update":
            log.changes = get_changes(log)
        elif log.action == "create":
            log.changes = safe_load(log.new_data)
        elif log.action == "delete":
            log.changes = safe_load(log.old_data)
        else:
            log.changes = None

    return render(request, "inventory/logs_list.html", {
        "logs": logs,
        "model": model,
        "object_id": object_id,
    })
