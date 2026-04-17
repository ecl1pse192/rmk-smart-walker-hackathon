from django.contrib import admin

from core.models import Defect, Equipment, Inspection, Reading, Route, Worker


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ("employee_number", "full_name", "role")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "shop", "normal_min", "normal_max")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "status")


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ("route", "worker", "started_at", "status")


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("inspection", "equipment", "value", "is_out_of_norm")


@admin.register(Defect)
class DefectAdmin(admin.ModelAdmin):
    list_display = ("equipment", "severity", "description")
