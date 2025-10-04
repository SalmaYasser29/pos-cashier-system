from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from .forms import ProfileImageForm
from branches.models import Branch
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from sales.models import Sale
from inventory.models import Category, Item
from customers.models import Customer
from branches.models import Branch
from django.utils.timezone import now


User = get_user_model()


# --- Login / Logout ---
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("accounts:dashboard")
        else:
            return render(request, "accounts/login.html", {"error": "Invalid credentials"})
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# --- Role checks ---
def is_super_admin(user):
    return user.is_authenticated and user.is_superuser


def is_branch_admin(user):
    return user.is_authenticated and user.role == "admin" and not user.is_superuser


# --- Add User ---
@login_required
def add_user_view(request):
    user = request.user

    if user.is_superuser:
        branches = Branch.objects.all()
    elif is_branch_admin(user):
        branches = Branch.objects.filter(id=user.branch.id)
    else:
        return HttpResponseForbidden("You are not authorized to add users.")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        role = request.POST.get("role")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        branch_id = user.branch.id if is_branch_admin(user) else request.POST.get("branch")

        if password1 != password2:
            return render(request, "accounts/add_user.html", {"error": "Passwords do not match", "branches": branches})
        if User.objects.filter(username=username).exists():
            return render(request, "accounts/add_user.html", {"error": "Username already exists", "branches": branches})
        if is_branch_admin(user) and role == "admin":
            return render(request, "accounts/add_user.html", {"error": "You cannot create another admin.", "branches": branches})

        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role,
            branch_id=branch_id,
            added_by=user
        )
        messages.success(request, f"User {username} added successfully.")
        return redirect("accounts:manage_users")

    return render(request, "accounts/add_user.html", {"branches": branches})



# --- Dashboard ---
@login_required
def dashboard(request):
    user = request.user

    # --- Superuser Dashboard (All branches) ---
    if user.is_superuser:
        sales_summary = (
            Sale.objects.values("datetime__date")
            .annotate(total=Sum("total"))
            .order_by("datetime__date")
        )

        context = {
            "total_users": User.objects.count(),
            "total_branches": Branch.objects.count(),
            "total_sales": Sale.objects.aggregate(total=Sum("total"))["total"] or 0,
            "low_stock_count": Item.objects.filter(stock__lt=5).count(),
            "sales_dates": [
                s["datetime__date"].strftime("%Y-%m-%d") for s in sales_summary
            ],
            "sales_values": [s["total"] for s in sales_summary],
        }
        return render(request, "accounts/dashboard_admin.html", context)

    # --- Admin Dashboard (Branch only) ---
    elif getattr(user, "role", None) == "admin":
        branch = user.branch
        sales = (
            Sale.objects.filter(branch=branch)
            .values("datetime__date")
            .annotate(total=Sum("total"))
            .order_by("datetime__date")
        )

        context = {
            "branch_name": branch.name if branch else "N/A",
            "branch_sales": Sale.objects.filter(branch=branch).aggregate(total=Sum("total"))["total"] or 0,
            "branch_customers": Customer.objects.filter(branch=branch).count(),
            "branch_items": Item.objects.filter(branch=branch).count(),
            "branch_categories": Category.objects.filter(branch=request.user.branch).count(),

            "branch_sales_dates": [
                s["datetime__date"].strftime("%Y-%m-%d") for s in sales
            ],
            "branch_sales_values": [s["total"] for s in sales],
        }
        return render(request, "accounts/dashboard_branch_admin.html", context)

    # --- Manager Dashboard (Branch only) ---
    elif getattr(user, "role", None) == "manager":
        branch = user.branch
        sales = (
            Sale.objects.filter(branch=branch)
            .values("datetime__date")
            .annotate(total=Sum("total"))
            .order_by("datetime__date")
        )

        context = {
            "branch_name": branch.name if branch else "N/A",
            "branch_sales": Sale.objects.filter(branch=branch).aggregate(total=Sum("total"))["total"] or 0,
            "branch_customers": Customer.objects.filter(branch=branch).count(),
            "branch_items": Item.objects.filter(branch=branch).count(),
            "branch_sales_dates": [
                s["datetime__date"].strftime("%Y-%m-%d") for s in sales
            ],
            "branch_sales_values": [s["total"] for s in sales],
        }
        return render(request, "accounts/dashboard_manager.html", context)

    # --- Cashier Dashboard (Own sales only) ---
    elif getattr(user, "role", None) == "cashier":
        branch = user.branch

        today = now().date()
        today_sales = (
            Sale.objects.filter(branch=branch, user=user, datetime__date=today)
            .aggregate(total=Sum("total"))["total"]
            or 0
        )

        context = {
            "todays_sales": today_sales,
            "payment_methods": [
                Sale.objects.filter(branch=branch, user=user, payment_method="cash").count(),
                Sale.objects.filter(branch=branch, user=user, payment_method="card").count(),
                Sale.objects.filter(branch=branch, user=user)
                .exclude(payment_method__in=["cash", "card"])
                .count(),
            ],
        }
        return render(request, "accounts/dashboard_cashier.html", context)

    # --- Default Fallback ---
    return render(request, "accounts/dashboard_default.html")


# --- Manage Users ---
@login_required
def manage_users(request):
    user = request.user
    if user.is_superuser:
        branches = Branch.objects.all()
        users_by_branch = {}
        for branch in branches:
            users_by_branch[branch] = User.objects.filter(branch=branch).exclude(id=user.id)
        return render(request, "accounts/manage_users.html", {"users_by_branch": users_by_branch})
    elif is_branch_admin(user):
        users = User.objects.filter(branch=user.branch).exclude(id=user.id)
        return render(request, "accounts/manage_users.html", {"users": users})
    else:
        return HttpResponseForbidden("You are not authorized to manage users.")


# --- Edit User ---
@login_required
def edit_user(request, user_id):
    current_user = request.user
    user_obj = get_object_or_404(User, id=user_id)

    # Permission check
    if current_user.is_superuser:
        branches = Branch.objects.all()
    elif is_branch_admin(current_user):
        if user_obj.branch != current_user.branch:
            messages.error(request, "You cannot edit users from other branches.")
            return redirect("accounts:manage_users")
        if user_obj.role == "admin":
            messages.error(request, "You cannot edit another admin.")
            return redirect("accounts:manage_users")
        branches = Branch.objects.filter(id=current_user.branch.id)
    else:
        messages.error(request, "You do not have permission to edit this user.")
        return redirect("accounts:manage_users")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        # Determine role
        if current_user.is_superuser:
            role = request.POST.get("role")
            if not role:
                messages.error(request, "Role is required.")
                return redirect("accounts:edit_user", user_id=user_id)
        else:
            # Branch admins cannot change role
            role = user_obj.role

        # Determine branch
        branch_id = request.POST.get("branch") if current_user.is_superuser else current_user.branch.id

        # Prevent branch admin from assigning admin role
        if is_branch_admin(current_user) and role == "admin":
            messages.error(request, "You cannot assign admin role.")
            return redirect("accounts:manage_users")

        # Save changes
        user_obj.username = username
        user_obj.email = email
        user_obj.role = role
        user_obj.branch_id = branch_id
        user_obj.save()

        messages.success(request, f"User {user_obj.username} updated successfully.")
        return redirect("accounts:manage_users")

    return render(request, "accounts/edit_user.html", {"user_obj": user_obj, "branches": branches})


# --- Delete User ---
@login_required
def delete_user(request, user_id):
    user = request.user
    user_obj = get_object_or_404(User, id=user_id)

    can_delete = user.is_superuser or (is_branch_admin(user) and user_obj.branch == user.branch and user_obj.role != "admin")
    if not can_delete:
        messages.error(request, "You do not have permission to delete this user.")
        return redirect("accounts:manage_users")

    user_obj.delete()
    messages.success(request, f"User {user_obj.username} deleted successfully.")
    return redirect("accounts:manage_users")


# --- Profile ---
@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user": request.user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileImageForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileImageForm(instance=request.user)

    return render(request, "accounts/edit_profile.html", {"form": form})


# --- Current User API ---
@login_required
def current_user(request):
    return JsonResponse({
        "username": request.user.username,
        "email": request.user.email,
        "role": request.user.role,
        "branch": request.user.branch.name if request.user.branch else None,
        "added_by": request.user.added_by.username if request.user.added_by else None
    })


# --- Branch Users ---
@login_required
def branch_users(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)

    query = request.GET.get("q", "").strip()
    users = User.objects.filter(branch=branch).select_related("branch", "added_by")

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(role__icontains=query) |
            Q(added_by__username__icontains=query)
        )

    paginator = Paginator(users, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "accounts/branch_users.html", {"page_obj": page_obj, "branch": branch, "ajax": True})

    return render(request, "accounts/branch_users.html", {"page_obj": page_obj, "branch": branch})
