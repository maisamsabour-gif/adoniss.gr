# Manually created migration for cover_image_slot.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0031_add_fa_name_tagline'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='cover_image_slot',
            field=models.PositiveSmallIntegerField(
                default=0,
                choices=[
                    (0, 'Auto — use first available photo'),
                    (1, 'Photo 1'),
                    (2, 'Photo 2'),
                    (3, 'Photo 3'),
                    (4, 'Photo 4'),
                    (5, 'Photo 5'),
                    (6, 'Photo 6'),
                    (7, 'Photo 7'),
                    (8, 'Photo 8'),
                    (9, 'Photo 9'),
                    (10, 'Photo 10'),
                    (11, 'Photo 11'),
                    (12, 'Photo 12'),
                    (13, 'Photo 13'),
                    (14, 'Photo 14'),
                    (15, 'Photo 15'),
                ],
                help_text=(
                    'Pick which of the 15 photos appears as the COVER on property cards '
                    '(homepage, properties list, related cards). '
                    'Set to "Auto" to use the first available photo.'
                ),
                verbose_name='Cover photo (card image)',
            ),
        ),
    ]
