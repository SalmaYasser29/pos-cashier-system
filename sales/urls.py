from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    path("", views.index, name="index"),
    path("pos/", views.pos, name="pos"),
    path("update_cart/<int:item_id>/", views.update_cart, name="update_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("history/", views.sale_history, name="sale_history"),
    path("today/", views.sales_today, name="sales_today"),
    path("sale_list/", views.sale_list, name="sales_list"),
    path("<int:pk>/", views.sale_detail, name="sale_detail"),
    path("detail/<int:pk>/", views.sale_detail, name="sale_detail_alt"),
    path("new/", views.sale_create, name="sale_create"),
    path("receipt/<int:sale_id>/", views.receipt_pdf, name="receipt_pdf"),
    path('customers/get_address/<int:customer_id>/', views.get_customer_address, name='get_customer_address'),
]
