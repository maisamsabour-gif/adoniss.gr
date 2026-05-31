"""
Migration 0027 — Privacy-map cleanup

Adds:
  • neighborhood_public / _en / _tr  — new public-facing neighborhood label for the map badge
  • area_en / area_tr               — modeltranslation variants for the existing `area` field
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0026_propertymedia_is_decorative'),
    ]

    operations = [

        # ── area translation variants ────────────────────────────────────────
        # `area` already exists as a plain CharField; we add the lang columns.
        migrations.AddField(
            model_name='property',
            name='area_en',
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name='District / Sub-area Label (Public)',
                help_text=(
                    'Optional secondary area shown on the card — e.g. "Alimos" or "Glyfada". '
                    'Keep it at district or neighbourhood level only; never a street address.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='area_tr',
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name='District / Sub-area Label (Public)',
                help_text=(
                    'Optional secondary area shown on the card — e.g. "Alimos" or "Glyfada". '
                    'Keep it at district or neighbourhood level only; never a street address.'
                ),
            ),
        ),

        # ── neighborhood_public (new field + translation variants) ───────────
        migrations.AddField(
            model_name='property',
            name='neighborhood_public',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='Public Neighborhood Label',
                help_text=(
                    'Shown next to the map circle on the property page — e.g. "Piraeus Port" '
                    'or "Glyfada Coast". Never use a street address here. '
                    'Leave blank to fall back to the general Area/Location.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='neighborhood_public_en',
            field=models.CharField(
                blank=True,
                max_length=200,
                null=True,
                verbose_name='Public Neighborhood Label',
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='neighborhood_public_tr',
            field=models.CharField(
                blank=True,
                max_length=200,
                null=True,
                verbose_name='Public Neighborhood Label',
            ),
        ),
    ]
