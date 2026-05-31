from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0025_seo_robots_fields'),
    ]

    operations = [
        # Rename verbose_name of caption (cosmetic — no DB column change needed).
        # The is_decorative column is the only real schema addition.
        migrations.AddField(
            model_name='propertymedia',
            name='is_decorative',
            field=models.BooleanField(
                default=False,
                verbose_name='Decorative image',
                help_text=(
                    'Tick if this image is a background fill, spacer, or purely visual decoration '
                    'that adds no meaningful information. The website will render alt="" for it, '
                    'which is correct accessibility practice.'
                ),
            ),
        ),
        # Update verbose_name / help_text on the existing caption column.
        migrations.AlterField(
            model_name='propertymedia',
            name='caption',
            field=models.CharField(
                max_length=200,
                blank=True,
                verbose_name='ALT Text',
                help_text=(
                    'Describe what is shown in this image for screen readers and search engines. '
                    'Example: "Modern living room with sea view, Alimos Athens". '
                    'Leave blank to fall back to the property name. '
                    'Tick "Decorative" below if the image is purely visual and needs no description.'
                ),
            ),
        ),
    ]
