# Generated by Django 4.2.6 on 2023-10-25 13:21

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
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
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                (
                    "cover",
                    models.CharField(
                        choices=[("HARD", "Hard"), ("SOFT", "Soft")],
                        default="HARD",
                        max_length=4,
                    ),
                ),
                ("inventory", models.PositiveIntegerField()),
                ("daily_fee", models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
    ]
