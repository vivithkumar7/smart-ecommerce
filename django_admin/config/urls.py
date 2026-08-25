from django.contrib import admin
from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.conf.urls.static import static
from adminapp.views import analytics_dashboard, export_report


def home(request):
    return redirect("admin:index")


urlpatterns = [
    path("admin/analytics/", admin.site.admin_view(analytics_dashboard), name="adminapp-analytics"),
    path("admin/reports/<str:report_type>/<str:file_format>/", admin.site.admin_view(export_report), name="adminapp-export"),
    path("admin/", admin.site.urls),
    path("", home, name="home"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
