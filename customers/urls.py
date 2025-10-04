from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.customer_create, name="customer_create"),
    path("<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("search/", views.customer_search, name="customer_search"),
]
