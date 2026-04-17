from __future__ import annotations

from typing import ClassVar, List, Type

from rest_framework import serializers

from core.models import Defect, Equipment, Inspection, Reading, Route, Worker


class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model: ClassVar[Type[Worker]] = Worker
        fields: ClassVar[List[str]] = ["id", "employee_number", "full_name", "role"]


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model: ClassVar[Type[Equipment]] = Equipment
        fields: ClassVar[List[str]] = [
            "id",
            "name",
            "shop",
            "normal_min",
            "normal_max",
        ]


class RouteSerializer(serializers.ModelSerializer):
    equipment = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Equipment.objects.all(),
        required=False,
    )

    class Meta:
        model: ClassVar[Type[Route]] = Route
        fields: ClassVar[List[str]] = ["id", "name", "equipment", "status"]


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model: ClassVar[Type[Inspection]] = Inspection
        fields: ClassVar[List[str]] = [
            "id",
            "route",
            "worker",
            "started_at",
            "ended_at",
            "status",
        ]


class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model: ClassVar[Type[Reading]] = Reading
        fields: ClassVar[List[str]] = [
            "id",
            "inspection",
            "equipment",
            "value",
            "instrument_photo",
            "is_out_of_norm",
        ]


class DefectSerializer(serializers.ModelSerializer):
    class Meta:
        model: ClassVar[Type[Defect]] = Defect
        fields: ClassVar[List[str]] = [
            "id",
            "equipment",
            "description",
            "photo",
            "severity",
        ]
