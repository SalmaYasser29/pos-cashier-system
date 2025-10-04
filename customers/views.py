from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Customer

# Only cashiers can access customers
def is_cashier(user):
    return user.is_authenticated and getattr(user, "role", None) == "cashier"

@login_required
def index(request):
    if not is_cashier(request.user):
        return HttpResponseForbidden("Only cashiers can manage customers.")

    customers = Customer.objects.filter(branch=request.user.branch)
    return render(request, "customers/index.html", {"customers": customers})

@login_required
def customer_create(request):
    if not is_cashier(request.user):
        return HttpResponseForbidden("Only cashiers can manage customers.")

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address", "")
        ctype = request.POST.get("type", "regular")

        customer = Customer.objects.create(
            name=name,
            phone=phone,
            address=address,
            customer_type=ctype,
            branch=request.user.branch
        )

        # If AJAX, return JSON
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "id": customer.id,
                "name": customer.name,
                "type": customer.customer_type
            })

        return redirect("customers:index")

    return render(request, "customers/form.html", {"form_title": "Add Customer"})

@login_required
def customer_edit(request, pk):
    if not is_cashier(request.user):
        return HttpResponseForbidden("Only cashiers can manage customers.")

    customer = get_object_or_404(Customer, pk=pk, branch=request.user.branch)

    if request.method == "POST":
        customer.name = request.POST.get("name")
        customer.phone = request.POST.get("phone")
        customer.address = request.POST.get("address", "")
        customer.customer_type = request.POST.get("type", "regular")
        customer.save()
        return redirect("customers:index")

    return render(request, "customers/form.html", {
        "customer": customer,
        "form_title": "Edit Customer"
    })

@login_required
def customer_search(request):
    if not is_cashier(request.user):
        return JsonResponse({"customers": []})

    q = request.GET.get("q", "")
    qs = Customer.objects.filter(branch=request.user.branch, name__icontains=q)[:20]
    data = [
        {"id": c.id, "name": c.name, "phone": c.phone, "type": c.customer_type}
        for c in qs
    ]
    return JsonResponse({"customers": data})
