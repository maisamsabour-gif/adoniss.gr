from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


def convert_float_to_int(apps, schema_editor):
    Page = apps.get_model('core', 'GoldenVisaFaLandingPage')
    for p in Page.objects.all():
        old = p.why_adonis_overlay_opacity
        if old is not None and old <= 1:
            p.why_adonis_overlay_opacity = int(round(old * 100))
        elif old is not None:
            p.why_adonis_overlay_opacity = min(int(round(old)), 100)
        else:
            p.why_adonis_overlay_opacity = 55
        p.save(update_fields=['why_adonis_overlay_opacity'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_goldenvisafa_why_adonis_bg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goldenvisafalandingpage',
            name='why_adonis_overlay_opacity',
            field=models.IntegerField(
                default=55,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name='تیرگی فیلتر روی تصویر (۰ تا ۱۰۰)',
                help_text='۰ = کاملاً شفاف (فقط تصویر)، ۱۰۰ = کاملاً تیره. پیشنهاد: ۴۰ تا ۶۰',
            ),
        ),
        migrations.RunPython(convert_float_to_int, migrations.RunPython.noop),
    ]
