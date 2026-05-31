from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0071_why_adonis_overlay_int'),
    ]

    operations = [
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='fa_whatsapp_number_2',
            field=models.CharField(
                blank=True, max_length=100,
                verbose_name='شماره یا لینک واتساپ دوم',
                help_text='شماره واتساپ دوم برای نمایش در فوتر. مثال: +306901234567 یا https://wa.me/306901234567',
            ),
        ),
    ]
