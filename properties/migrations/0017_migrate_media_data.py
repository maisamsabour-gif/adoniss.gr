"""
Step 2 of 3 – copy data from the legacy image/video columns and the old
PropertyImage table into PropertyMedia rows.

Mapping:
  Property.main_image  → PropertyMedia(is_cover=True,  order=0)
  Property.image_2..20 → PropertyMedia(is_cover=False, order=2..20)
  Property.video       → PropertyMedia(video=…, poster=video_poster, order=100)
  PropertyImage rows   → PropertyMedia(order=200+original_order)
"""
from django.db import migrations


OLD_IMAGE_FIELDS = [
    ('main_image', 0, True),
    ('image_2',  2,  False),
    ('image_3',  3,  False),
    ('image_4',  4,  False),
    ('image_5',  5,  False),
    ('image_6',  6,  False),
    ('image_7',  7,  False),
    ('image_8',  8,  False),
    ('image_9',  9,  False),
    ('image_10', 10, False),
    ('image_11', 11, False),
    ('image_12', 12, False),
    ('image_13', 13, False),
    ('image_14', 14, False),
    ('image_15', 15, False),
    ('image_16', 16, False),
    ('image_17', 17, False),
    ('image_18', 18, False),
    ('image_19', 19, False),
    ('image_20', 20, False),
]


def forwards(apps, schema_editor):
    Property = apps.get_model('properties', 'Property')
    PropertyMedia = apps.get_model('properties', 'PropertyMedia')
    PropertyImage = apps.get_model('properties', 'PropertyImage')

    for prop in Property.objects.all():
        # ── direct image slots ──────────────────────────────────────────────
        for field_name, order, is_cover in OLD_IMAGE_FIELDS:
            path = getattr(prop, field_name, None)
            if path:
                PropertyMedia.objects.create(
                    property=prop,
                    image=path,
                    is_cover=is_cover,
                    order=order,
                )

        # ── video + poster ──────────────────────────────────────────────────
        video_path = getattr(prop, 'video', None)
        if video_path:
            poster_path = getattr(prop, 'video_poster', None) or ''
            PropertyMedia.objects.create(
                property=prop,
                video=video_path,
                poster=poster_path,
                order=100,
            )

        # ── legacy PropertyImage rows ───────────────────────────────────────
        for pi in PropertyImage.objects.filter(property=prop).order_by('order'):
            if pi.image:
                PropertyMedia.objects.create(
                    property=prop,
                    image=pi.image,
                    caption=pi.caption or '',
                    order=200 + pi.order,
                )


def backwards(apps, schema_editor):
    PropertyMedia = apps.get_model('properties', 'PropertyMedia')
    PropertyMedia.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0016_add_propertymedia'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
