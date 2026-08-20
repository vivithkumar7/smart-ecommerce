from django.contrib import admin
from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.conf.urls.static import static


def home(request):
    return redirect("admin:index")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
