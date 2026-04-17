from __future__ import annotations

import base64
import logging
import os
import re
from decimal import Decimal

import requests
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework import serializers
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

logger = logging.getLogger(__name__)

def _extract_text_from_ocr_response(data: object) -> str:
    texts: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in {"text", "fullText", "full_text"} and isinstance(v, str):
                    texts.append(v)
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    merged = "\n".join(t.strip() for t in texts if t and t.strip())
    if merged.strip():
        return merged

    if isinstance(data, dict):
        for k in ("result", "results", "textDetection", "text_detection", "text"):
            v = data.get(k)
            if isinstance(v, str) and v.strip():
                return v

    return ""


def recognize_value_from_image(photo_file: object | None) -> Decimal:
    if photo_file is None:
        raise serializers.ValidationError("Фото прибора не передано.")

    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    folder_id = os.getenv("YANDEX_FOLDER_ID", "").strip()
    if not api_key or not folder_id:
        raise serializers.ValidationError(
            "Не настроены переменные окружения YANDEX_API_KEY / YANDEX_FOLDER_ID."
        )

    content_type = getattr(photo_file, "content_type", None) or "image/jpeg"
    try:
        raw = photo_file.read()
    except Exception as exc:
        raise serializers.ValidationError("Не удалось прочитать файл изображения.") from exc

    b64 = base64.b64encode(raw).decode("ascii")

    url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"
    payload = {
        "mimeType": content_type,
        "languageCodes": ["ru", "en"],
        "model": "page",
        "content": b64,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}",
        "x-folder-id": folder_id,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=20)
    except requests.RequestException as exc:
        raise serializers.ValidationError("Ошибка сети при обращении к OCR сервису.") from exc

    if resp.status_code != 200:
        preview = resp.text[:2000] if resp.text else ""
        logger.warning(
            "Yandex OCR error status=%s body_preview=%r",
            resp.status_code,
            preview,
        )
        raise serializers.ValidationError("Ошибка сервиса распознавания.")

    try:
        data = resp.json()
    except ValueError as exc:
        logger.warning("Yandex OCR non-JSON response preview=%r", (resp.text or "")[:2000])
        raise serializers.ValidationError("OCR сервис вернул некорректный ответ.") from exc

    text = _extract_text_from_ocr_response(data)
    logger.info("Yandex OCR text_preview=%r", text[:500])

    m = re.search(r"(\d+(?:[.,]\d+)?)", text)
    if not m:
        raise serializers.ValidationError(
            "Не удалось распознать значение на фото. Пожалуйста, переснимите."
        )

    num = m.group(1).replace(",", ".")
    try:
        return Decimal(num)
    except Exception as exc:
        raise serializers.ValidationError(
            "Не удалось распарсить распознанное значение. Пожалуйста, переснимите."
        ) from exc


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
        value = recognize_value_from_image(photo)
        is_out_of_norm = value < equipment.normal_min or value > equipment.normal_max

        serializer.save(value=value, is_out_of_norm=is_out_of_norm, instrument_photo=photo)


class DefectViewSet(viewsets.ModelViewSet):
    queryset = Defect.objects.select_related("equipment").all()
    serializer_class = DefectSerializer

def master_dashboard(request):
    return render(request, 'master.html')