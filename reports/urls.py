from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_dashboard, name="dashboard"),
    path("sales_trends/<str:period>/", views.sales_trends, name="sales_trends"),
    path("sales_trends_range/", views.sales_trends_range, name="sales_trends_range"),
    path("top_items/", views.top_items, name="top_items"),
    path("low_stock/", views.low_stock, name="low_stock"),
    path("export/csv/", views.export_sales_csv, name="export_sales_csv"),
    path("export/pdf/", views.export_sales_pdf, name="export_sales_pdf"),
    path("sales-pdf/<int:branch_id>/", views.sales_pdf, name="sales_pdf"),
]
