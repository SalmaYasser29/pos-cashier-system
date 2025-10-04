from django.urls import path
from . import views

app_name = "branches"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.branch_create, name="branch_create"),
    path("<int:branch_id>/edit/", views.branch_edit, name="branch_edit"),
    path("<int:branch_id>/delete/", views.branch_delete, name="branch_delete"),
    path("json/", views.branch_list_json, name="branch_list_json"),
]
