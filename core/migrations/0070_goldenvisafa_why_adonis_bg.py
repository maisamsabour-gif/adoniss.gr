from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0069_goldenvisafa_why_adonis'),
    ]

    operations = [
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_adonis_bg_image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='golden_visa_fa_landing/',
                verbose_name='تصویر پس‌زمینه سکشن «چرا آدونیس؟»',
                help_text='اگر آپلود نشود، پس‌زمینه رنگی Navy نمایش داده می‌شود. '
                          'اندازه پیشنهادی: ۱۹۲۰×۸۰۰ پیکسل.',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_adonis_overlay_opacity',
            field=models.FloatField(
                default=0.72,
                verbose_name='تیرگی فیلتر روی تصویر (۰ تا ۱)',
                help_text='عدد بین ۰ (شفاف کامل) تا ۱ (تیره کامل). پیشنهاد: ۰.۶ تا ۰.۸',
            ),
        ),
    ]
