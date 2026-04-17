from __future__ import annotations

from rest_framework import viewsets

from core.models import Defect, Equipment, Inspection, Reading, Route, Worker
from core.serializers import (
    DefectSerializer,
    EquipmentSerializer,
    InspectionSerializer,
    ReadingSerializer,
    RouteSerializer,
    WorkerSerializer,
)


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer


class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.prefetch_related("equipment").all()
    serializer_class = RouteSerializer


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.select_related("route", "worker").all()
    serializer_class = InspectionSerializer


class ReadingViewSet(viewsets.ModelViewSet):
    queryset = Reading.objects.select_related("inspection", "equipment").all()
    serializer_class = ReadingSerializer


class DefectViewSet(viewsets.ModelViewSet):
    queryset = Defect.objects.select_related("equipment").all()
    serializer_class = DefectSerializer
