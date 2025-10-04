from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Only superuser/admin can access this (restricted in views)
    path("add_user/", views.add_user_view, name="add_user"),
    path("manage_users/", views.manage_users, name="manage_users"),
    path("edit_user/<int:user_id>/", views.edit_user, name="edit_user"), 
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("users/branch/<int:branch_id>/", views.branch_users, name="branch_users"),     

    # Profile Picture
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # API endpoint for fetching current user info
    path("me/", views.current_user, name="current_user"),
]

