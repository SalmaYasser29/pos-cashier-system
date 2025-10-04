import json
from decimal import Decimal
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from inventory.models import Item, Category
from customers.models import Customer
from .models import Sale, SaleItem

from xhtml2pdf import pisa
from django.template.loader import get_template
import io


# -------------------------------
# POS Home / index
# -------------------------------
@login_required
def index(request):
    return render(request, "sales/pos.html")


@login_required
def pos(request):
    """Point of Sale screen filtered by user branch"""
    branch = getattr(request.user, "branch", None)

    if branch:
        items = Item.objects.select_related("category").filter(branch=branch, stock__gt=0)
        categories = Category.objects.filter(item__branch=branch).distinct()
        customers = Customer.objects.filter(branch=branch)
    else:
        items = Item.objects.none()
        categories = Category.objects.none()
        customers = Customer.objects.none()

    return render(request, "sales/pos.html", {
        "items": items,
        "categories": categories,
        "customers": customers,
        "branch": branch,
    })


# -------------------------------
# Checkout API
# -------------------------------
@login_required
@csrf_exempt
def checkout(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    items_data = payload.get("items", [])
    customer_id = payload.get("customer_id")
    order_type = payload.get("order_type", "dine_in")
    payment_method = payload.get("payment_method", "cash")

    try:
        discount_percent = Decimal(payload.get("discount", 0))
        cash_amount = Decimal(payload.get("cash_amount", 0))
        card_amount = Decimal(payload.get("card_amount", 0))
    except Exception:
        return JsonResponse({"error": "Invalid numeric values"}, status=400)

    if not items_data:
        return JsonResponse({"error": "Cart is empty"}, status=400)

    customer = None
    if customer_id:
        try:
            customer = Customer.objects.get(pk=int(customer_id))
        except Customer.DoesNotExist:
            return JsonResponse({"error": "Invalid customer"}, status=400)

    branch = getattr(request.user, "branch", None)
    if not branch:
        return JsonResponse({"error": "User has no assigned branch"}, status=400)

    table_number = payload.get("table_number") if order_type == "dine_in" else None
    if order_type == "dine_in" and not table_number:
        return JsonResponse({"error": "Please enter a table number for dine-in orders"}, status=400)

    try:
        with transaction.atomic():
            sale = Sale.objects.create(
                user=request.user,
                branch=branch,
                customer=customer,
                order_type=order_type,
                table_number=table_number,
                payment_method=payment_method,
                discount_percent=discount_percent,
                cash_amount=cash_amount if payment_method == "mixed" else None,
                card_amount=card_amount if payment_method == "mixed" else None,
            )

            total = Decimal("0.00")

            for it in items_data:
                try:
                    item = Item.objects.select_for_update().get(pk=int(it["id"]))
                except Item.DoesNotExist:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": f"Item not found: {it['id']}"}, status=400)

                qty = int(it["quantity"])
                if item.stock < qty:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": f"Insufficient stock for item: {item.name}"}, status=400)

                item.stock -= qty
                item.save()

                SaleItem.objects.create(
                    sale=sale,
                    item=item,
                    quantity=qty,
                    price=item.price
                )

                total += item.price * qty

            discount_amount = (total * discount_percent / 100).quantize(Decimal("0.01"))
            final_total = (total - discount_amount).quantize(Decimal("0.01"))

            if payment_method == "mixed":
                if cash_amount + card_amount != final_total:
                    transaction.set_rollback(True)
                    return JsonResponse({"error": "Cash + Card amount must equal final total"}, status=400)

            sale.total = total.quantize(Decimal("0.01"))
            sale.discount_amount = discount_amount
            sale.final_total = final_total
            sale.save()

            return JsonResponse({
                "sale_id": sale.id,
                "total": str(sale.total),
                "final_total": str(sale.final_total),
                "discount_percent": str(sale.discount_percent),
                "discount_amount": str(sale.discount_amount),
                "redirect_url": reverse("sales:sale_detail", args=[sale.id])
            })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# -------------------------------
# Get customer address via AJAX
# -------------------------------
@login_required
def get_customer_address(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
        return JsonResponse({"address": customer.address})
    except Customer.DoesNotExist:
        return JsonResponse({"address": ""})


# -------------------------------
# Sale list / history for logged-in user
# -------------------------------
@login_required
def sale_list(request):
    sales = Sale.objects.select_related("customer", "branch", "user") \
                        .filter(user=request.user) \
                        .order_by("-datetime")
    for s in sales:
        s.datetime = timezone.localtime(s.datetime)
    return render(request, "sales/sale_list.html", {"sales": sales})


@login_required
def sale_history(request):
    sales = Sale.objects.select_related("customer", "branch", "user").order_by("-datetime")[:50]
    for s in sales:
        s.datetime = timezone.localtime(s.datetime)
    return render(request, "sales/history.html", {"sales": sales})


# -------------------------------
# Sale detail
# -------------------------------
@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    sale.datetime = timezone.localtime(sale.datetime)
    return render(request, "sales/detail.html", {"sale": sale})


# -------------------------------
# Manual sale creation (form)
# -------------------------------
@login_required
def sale_create(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer")
        payment_method = request.POST.get("payment_method", "cash")
        total = Decimal(request.POST.get("total", 0))
        order_type = request.POST.get("order_type", "dine_in")

        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(pk=int(customer_id))
            except Customer.DoesNotExist:
                customer = None

        sale = Sale.objects.create(
            user=request.user,
            branch=getattr(request.user, "branch", None),
            customer=customer,
            payment_method=payment_method,
            order_type=order_type,
            total=total
        )

        items = request.POST.getlist("items")
        quantities = request.POST.getlist("quantities")

        for item_id, qty in zip(items, quantities):
            item = Item.objects.get(pk=item_id)
            SaleItem.objects.create(
                sale=sale,
                item=item,
                quantity=int(qty),
                price=item.price
            )
            item.stock -= int(qty)
            item.save()

        return redirect("sales:pos")

    branch = getattr(request.user, "branch", None)
    customers = Customer.objects.filter(branch=branch) if branch else Customer.objects.none()

    return render(request, "sales/sale_form.html", {
        "items": Item.objects.all(),
        "customers": customers
    })


# -------------------------------
# Receipt PDF
# -------------------------------
@login_required
def receipt_pdf(request, sale_id):
    sale = get_object_or_404(Sale, pk=sale_id)
    sale.datetime = timezone.localtime(sale.datetime)

    total_before_discount = sale.total.quantize(Decimal("0.01"))
    discount_amount = sale.discount_amount.quantize(Decimal("0.01"))
    total_after_discount = sale.final_total.quantize(Decimal("0.01"))

    template = get_template('sales/receipt.html')
    html = template.render({
        'sale': sale,
        'total_before_discount': total_before_discount,
        'discount_amount': discount_amount,
        'total_after_discount': total_after_discount,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="receipt_{sale.id}.pdf"'

    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response


# -------------------------------
# Today's sales for the logged-in user
# -------------------------------
@login_required
def sales_today(request):
    today = timezone.localdate()
    sales = Sale.objects.filter(
        user=request.user,
        datetime__date=today
    ).order_by("-datetime")
    for s in sales:
        s.datetime = timezone.localtime(s.datetime)
    return render(request, "sales/sales_today.html", {"sales": sales})


# -------------------------------
# - & + buttons
# -------------------------------
@require_POST
def update_cart(request, item_id):
    cart = request.session.get("cart", {})

    if str(item_id) in cart:
        if request.POST.get("action") == "increase":
            cart[str(item_id)]["qty"] += 1
        elif request.POST.get("action") == "decrease":
            cart[str(item_id)]["qty"] -= 1
            if cart[str(item_id)]["qty"] <= 0:
                del cart[str(item_id)]

    request.session["cart"] = cart
    return redirect("pos")
