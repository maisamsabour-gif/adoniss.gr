from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [('core', '0056_goldenvisafalandingpage')]

    operations = [
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='hero_image_opacity',
            field=models.PositiveIntegerField(
                default=70,
                validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)],
            ),
        ),
    ]
