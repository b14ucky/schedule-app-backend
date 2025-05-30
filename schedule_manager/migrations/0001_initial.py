# Generated by Django 5.2 on 2025-04-14 22:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeSchedule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("month", models.IntegerField()),
                ("year", models.IntegerField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Shift",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("time_start", models.TimeField(blank=True, null=True)),
                ("time_end", models.TimeField(blank=True, null=True)),
                (
                    "day_type",
                    models.CharField(
                        choices=[
                            ("WORK", "Praca"),
                            ("SICK_LEAVE", "L4"),
                            ("VACATION", "Urlop"),
                            ("NON_WORKING_DAY", "Dzień wolny (grafik)"),
                            ("AVAILABILITY_OFF", "Wolne (niedyspozycyjność)"),
                            ("REQUESTED_OFF", "Wolne na prośbę"),
                        ],
                        default="NON_WORKING_DAY",
                        max_length=20,
                    ),
                ),
                (
                    "additional_info",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "schedule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="schedule_manager.employeeschedule",
                    ),
                ),
            ],
        ),
    ]
