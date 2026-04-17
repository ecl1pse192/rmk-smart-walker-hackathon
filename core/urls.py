from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core import views

router = DefaultRouter()
router.register(r"workers", views.WorkerViewSet, basename="worker")
router.register(r"equipment", views.EquipmentViewSet, basename="equipment")
router.register(r"routes", views.RouteViewSet, basename="route")
router.register(r"inspections", views.InspectionViewSet, basename="inspection")
router.register(r"readings", views.ReadingViewSet, basename="reading")
router.register(r"defects", views.DefectViewSet, basename="defect")

urlpatterns = [
    path("", include(router.urls)),
]
