from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from core.views import master_dashboard

urlpatterns = [
    path("", ensure_csrf_cookie(TemplateView.as_view(template_name="index.html"))),
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path('master/', master_dashboard, name='master-dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
