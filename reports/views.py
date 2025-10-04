from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils.dateparse import parse_date
import csv
import datetime

from sales.models import Sale, SaleItem
from inventory.models import Item
from branches.models import Branch


def _resolve_branch_for_request(request):
    """
    Resolve branch to use for reports:
    - If ?branch_id= is provided and user is admin/superuser -> use it.
    - If no branch_id provided -> use request.user.branch (if set).
    - If a non-admin provides branch_id different from their branch -> forbidden.
    Returns branch instance or None.
    """
    branch_id = request.GET.get("branch_id") or request.POST.get("branch_id")
    user_branch = getattr(request.user, "branch", None)

    if branch_id:
        try:
            branch = Branch.objects.get(pk=int(branch_id))
        except (Branch.DoesNotExist, ValueError):
            return None
        # if user is superuser or has admin role allow any branch
        is_admin = getattr(request.user, "is_superuser", False) or getattr(request.user, "role", "") == "admin"
        if is_admin:
            return branch
        # otherwise only allow user's own branch
        if user_branch and branch.id == user_branch.id:
            return branch
        # forbidden
        return None
    # no branch_id -> fallback to user's branch
    return user_branch


# --- Dashboard page ---
@login_required
def reports_dashboard(request):
    """
    Render the reports dashboard. It will show UI; the JS will call APIs
    passing branch_id (from request.user.branch by default).
    """
    branch = _resolve_branch_for_request(request)
    # If branch resolution failed (e.g. non-admin requested a different branch), show their branch or a message
    if branch is None and getattr(request.user, "branch", None) is None:
        # no branch found for user: still render — JS will call endpoints without branch_id and backend will return empty sets
        branch = None

    return render(request, "reports/dashboard.html", {"branch": branch})


# --- Helper: sales queryset for resolved branch ---
def get_branch_sales_qs(request):
    branch = _resolve_branch_for_request(request)
    if branch is None:
        # If branch param was provided but not allowed, return empty queryset
        # If no branch at all (user not assigned), also return empty
        return Sale.objects.none()
    return Sale.objects.filter(branch=branch)


# --- API: Sales trends (daily/weekly/monthly/yearly) ---
@login_required
def sales_trends(request, period):
    """
    Query params:
      - branch_id (optional)
    path param:
      - period: daily | weekly | monthly | yearly
    Returns JSON: { labels: [...], totals: [...] }
    """
    qs = get_branch_sales_qs(request)

    if period == "daily":
        qs = qs.annotate(date=TruncDay("datetime"))
    elif period == "weekly":
        qs = qs.annotate(date=TruncWeek("datetime"))
    elif period == "monthly":
        qs = qs.annotate(date=TruncMonth("datetime"))
    elif period == "yearly":
        qs = qs.annotate(date=TruncYear("datetime"))
    else:
        return JsonResponse({"labels": [], "totals": []})

    qs = qs.values("date").annotate(total=Sum("final_total")).order_by("date")

    labels = []
    totals = []
    for row in qs:
        dt = row.get("date")
        total = row.get("total") or 0
        # dt may be None in weird cases; guard
        if isinstance(dt, (datetime.date, datetime.datetime)):
            labels.append(dt.strftime("%Y-%m-%d"))
        else:
            labels.append(str(dt))
        totals.append(float(total))

    return JsonResponse({"labels": labels, "totals": totals})


# --- API: Sales trends by custom date range ---
@login_required
def sales_trends_range(request):
    """
    Query params:
      - start=YYYY-MM-DD
      - end=YYYY-MM-DD
      - branch_id (optional)
    """
    start = request.GET.get("start")
    end = request.GET.get("end")
    if not start or not end:
        return JsonResponse({"labels": [], "totals": []})

    try:
        start_date = parse_date(start)
        end_date = parse_date(end)
        if start_date is None or end_date is None:
            raise ValueError("Invalid date")
    except Exception:
        return JsonResponse({"labels": [], "totals": []})

    qs = get_branch_sales_qs(request).filter(datetime__date__range=[start_date, end_date])
    qs = qs.annotate(date=TruncDay("datetime")).values("date").annotate(total=Sum("final_total")).order_by("date")

    labels = [x["date"].strftime("%Y-%m-%d") for x in qs]
    totals = [float(x["total"] or 0) for x in qs]
    return JsonResponse({"labels": labels, "totals": totals})


# --- API: Top selling items ---
@login_required
def top_items(request):
    """
    Query params:
      - branch_id (optional)
    Returns top 5 items for the branch (labels and totals)
    """
    branch = _resolve_branch_for_request(request)
    if branch is None:
        return JsonResponse({"labels": [], "totals": []})

    qs = (
        SaleItem.objects.filter(sale__branch=branch)
        .values("item__name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:10]
    )

    labels = [x["item__name"] for x in qs]
    totals = [int(x["total_qty"] or 0) for x in qs]
    return JsonResponse({"labels": labels, "totals": totals})


# --- API: Low stock items ---
@login_required
def low_stock(request):
    """
    Query params:
      - branch_id (optional)
    Returns small list of items in that branch with stock <= threshold
    """
    branch = _resolve_branch_for_request(request)
    if branch is None:
        return JsonResponse({"items": []})

    threshold = request.GET.get("threshold")
    try:
        threshold = int(threshold) if threshold is not None else 10
    except Exception:
        threshold = 10

    items = Item.objects.filter(branch=branch, stock__lte=threshold).order_by("stock")[:50]
    data = [{"name": i.name, "stock": i.stock} for i in items]
    return JsonResponse({"items": data})


# --- Export: CSV ---
@login_required
def export_sales_csv(request):
    branch = _resolve_branch_for_request(request)
    if branch is None:
        return HttpResponseForbidden("Not allowed or no branch selected")

    start = request.GET.get("start")
    end = request.GET.get("end")
    sales = Sale.objects.filter(branch=branch)
    if start and end:
        sales = sales.filter(datetime__date__range=[start, end])

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="sales_report_{branch.name}.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Date", "Customer", "Total Before Discount", "Discount", "Final Total", "Payment Method"])

    for sale in sales.order_by("-datetime"):
        writer.writerow([
            sale.id,
            sale.datetime.strftime("%Y-%m-%d %H:%M"),
            str(sale.customer) if sale.customer else "Walk-in",
            f"{sale.total:.2f}",
            f"{sale.discount_amount:.2f}",
            f"{sale.final_total:.2f}",
            sale.payment_method,
        ])
    return response


# --- Export: PDF (xhtml2pdf) ---
@login_required
def export_sales_pdf(request):
    branch = _resolve_branch_for_request(request)
    if branch is None:
        return HttpResponseForbidden("Not allowed or no branch selected")

    start = request.GET.get("start")
    end = request.GET.get("end")
    sales = Sale.objects.filter(branch=branch)
    if start and end:
        sales = sales.filter(datetime__date__range=[start, end])

    template = get_template("reports/sales_pdf.html")
    html = template.render({"sales": sales, "branch": branch})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="sales_report_{branch.name}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response


# --- Inline PDF view (for one branch) ---
@login_required
def sales_pdf(request, branch_id):
    # Only allow if admin or branch owner
    try:
        branch = Branch.objects.get(pk=branch_id)
    except Branch.DoesNotExist:
        return HttpResponse("Branch not found", status=404)

    # permission check
    is_admin = getattr(request.user, "is_superuser", False) or getattr(request.user, "role", "") == "admin"
    user_branch = getattr(request.user, "branch", None)
    if not is_admin and (user_branch is None or user_branch.id != branch.id):
        return HttpResponseForbidden("Not allowed")

    sales = Sale.objects.filter(branch=branch).order_by("-datetime")
    template = get_template("reports/sales_pdf.html")
    html = template.render({"sales": sales, "branch": branch})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="sales_{branch.name}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response
