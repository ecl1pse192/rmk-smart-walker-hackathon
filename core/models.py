from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import models


class Worker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField("Табельный номер", max_length=32, unique=True)
    full_name = models.CharField("ФИО", max_length=255)
    role = models.CharField("Роль", max_length=128)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["full_name"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.employee_number})"


class Equipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Название", max_length=255)
    shop = models.CharField("Цех", max_length=128)
    normal_min = models.DecimalField(
        "Норма от",
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )
    normal_max = models.DecimalField(
        "Норма до",
        max_digits=14,
        decimal_places=4,
        default=Decimal("0"),
    )

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"
        ordering = ["shop", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.shop})"


class Route(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        ACTIVE = "active", "Активен"
        ARCHIVED = "archived", "Архив"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Название", max_length=255)
    equipment = models.ManyToManyField(
        Equipment,
        verbose_name="Оборудование",
        related_name="routes",
        blank=True,
    )
    status = models.CharField(
        "Статус",
        max_length=32,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Inspection(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Запланирован"
        IN_PROGRESS = "in_progress", "В процессе"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        Route,
        verbose_name="Маршрут",
        on_delete=models.CASCADE,
        related_name="inspections",
    )
    worker = models.ForeignKey(
        Worker,
        verbose_name="Сотрудник",
        on_delete=models.PROTECT,
        related_name="inspections",
    )
    started_at = models.DateTimeField("Время начала")
    ended_at = models.DateTimeField("Время окончания", null=True, blank=True)
    status = models.CharField(
        "Статус",
        max_length=32,
        choices=Status.choices,
        default=Status.PLANNED,
    )

    class Meta:
        verbose_name = "Обход"
        verbose_name_plural = "Обходы"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.route} — {self.started_at:%Y-%m-%d %H:%M}"


class Reading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(
        Inspection,
        verbose_name="Обход",
        on_delete=models.CASCADE,
        related_name="readings",
    )
    equipment = models.ForeignKey(
        Equipment,
        verbose_name="Оборудование",
        on_delete=models.CASCADE,
        related_name="readings",
    )
    value = models.DecimalField("Считанное значение", max_digits=14, decimal_places=4)
    instrument_photo = models.ImageField(
        "Фото прибора",
        upload_to="readings/instruments/",
        blank=True,
        null=True,
    )
    is_out_of_norm = models.BooleanField("Отклонение от нормы", default=False)

    class Meta:
        verbose_name = "Показание"
        verbose_name_plural = "Показания"
        ordering = ["inspection", "equipment"]

    def __str__(self) -> str:
        return f"{self.equipment} = {self.value}"


class Defect(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Низкая"
        MEDIUM = "medium", "Средняя"
        HIGH = "high", "Высокая"
        CRITICAL = "critical", "Критическая"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(
        Equipment,
        verbose_name="Оборудование",
        on_delete=models.CASCADE,
        related_name="defects",
    )
    description = models.TextField("Описание")
    photo = models.ImageField(
        "Фото",
        upload_to="defects/",
        blank=True,
        null=True,
    )
    severity = models.CharField(
        "Критичность",
        max_length=32,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )

    class Meta:
        verbose_name = "Дефект"
        verbose_name_plural = "Дефекты"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.equipment}: {self.description[:50]}"
