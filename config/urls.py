from django.contrib import admin
from django.urls import include, path

urlpatterns = [path("admin/", admin.site.urls), path("accounts/", include("backend.accounts.urls")), path("", include("backend.workspace.urls"))]
handler400 = "backend.workspace.views.error_400"
handler403 = "backend.workspace.views.error_403"
handler404 = "backend.workspace.views.error_404"
handler500 = "backend.workspace.views.error_500"
