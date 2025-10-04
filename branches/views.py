from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Branch
from django.db.models import ProtectedError


def is_admin(user):
    return user.is_authenticated and user.is_superuser

# -------------------------------
# List all branches
# -------------------------------
@login_required
def index(request):
    branches = Branch.objects.all()
    return render(request, "branches/index.html", {"branches": branches})

# -------------------------------
# Create new branch
# -------------------------------
@login_required
@user_passes_test(is_admin)
def branch_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        city = request.POST.get("city")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        website = request.POST.get("website")

        if name:
            Branch.objects.create(
                name=name,
                address=address,
                city=city,
                phone=phone,
                email=email,
                website=website
            )
            return redirect("branches:index")

    return render(request, "branches/form.html", {"form_title": "Add New Branch"})

# -------------------------------
# Edit branch
# -------------------------------
@login_required
@user_passes_test(is_admin)
def branch_edit(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    if request.method == "POST":
        branch.name = request.POST.get("name")
        branch.address = request.POST.get("address")
        branch.city = request.POST.get("city")
        branch.phone = request.POST.get("phone")
        branch.email = request.POST.get("email")
        branch.website = request.POST.get("website")
        branch.save()
        return redirect("branches:index")

    return render(request, "branches/form.html", {
        "form_title": "Edit Branch",
        "branch": branch
    })

# -------------------------------
# Delete branch
# -------------------------------
@login_required
@user_passes_test(is_admin)
def branch_delete(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    if request.method == "POST":
        try:
            branch.delete()
            return redirect("branches:index")
        except ProtectedError as e:
            # Get a list of related objects causing the issue
            related_objects = []
            for obj_set in e.protected_objects:
                related_objects.append(str(obj_set))
            
            return render(request, "branches/cannot_delete.html", {
                "branch": branch,
                "reason": related_objects
            })
    return render(request, "branches/confirm_delete.html", {"branch": branch})

# -------------------------------
# JSON output for all branches
# -------------------------------
@login_required
def branch_list_json(request):
    data = [
        {
            "id": b.id,
            "name": b.name,
            "address": b.address,
            "city": b.city,
            "phone": b.phone,
            "email": b.email,
            "website": b.website
        }
        for b in Branch.objects.all()
    ]
    return JsonResponse({"branches": data})
