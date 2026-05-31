from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0098_fix_section_types_and_orders'),
    ]

    operations = [
        migrations.AddField(
            model_name='fanewsection',
            name='background_image_opacity',
            field=models.PositiveIntegerField(
                default=50,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name='شفافیت تصویر پس‌زمینه (%)',
                help_text='۰ = کاملاً پنهان · ۱۰۰ = کاملاً نمایان. پیشنهاد: ۳۰ تا ۷۰',
            ),
        ),
    ]
