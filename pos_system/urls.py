"""
URL configuration for pos_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
# for media files
from django.conf import settings
from django.conf.urls.static import static

def root_redirect(request):
    return redirect("accounts:login")


urlpatterns = [
    path("", root_redirect, name="root"),  
    path("admin/", admin.site.urls),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("branches/", include(("branches.urls", "branches"), namespace="branches")),
    path("customers/", include(("customers.urls", "customers"), namespace="customers")),
    path("inventory/", include(("inventory.urls", "inventory"), namespace="inventory")),
    path("reports/", include(("reports.urls", "reports"), namespace="reports")),
    path("sales/", include(("sales.urls", "sales"), namespace="sales")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
