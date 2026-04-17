from __future__ import annotations

import random
from decimal import Decimal

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer

from core.models import Defect, Equipment, Inspection, Reading, Route, Worker
from core.serializers import (
    DefectSerializer,
    EquipmentSerializer,
    InspectionSerializer,
    ReadingSerializer,
    RouteSerializer,
    WorkerSerializer,
)


def mock_recognize_value_from_image(photo: object | None) -> Decimal:
    _ = photo
    return Decimal(str(round(random.uniform(0, 100), 4)))


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

    def perform_create(self, serializer: BaseSerializer) -> None:
        request: Request = self.request
        photo = request.FILES.get("instrument_photo")

        equipment: Equipment = serializer.validated_data["equipment"]
        value = mock_recognize_value_from_image(photo)
        is_out_of_norm = value < equipment.normal_min or value > equipment.normal_max

        serializer.save(value=value, is_out_of_norm=is_out_of_norm)


class DefectViewSet(viewsets.ModelViewSet):
    queryset = Defect.objects.select_related("equipment").all()
    serializer_class = DefectSerializer
