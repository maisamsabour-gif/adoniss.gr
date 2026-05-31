from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0072_fa_whatsapp_number_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutpagesettings',
            name='hero_image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='about/',
                verbose_name='تصویر Hero (About Us)',
                help_text='تصویر پس‌زمینه بخش Hero صفحه «درباره ما». اگر آپلود نشود، گرادیان آبی نمایش داده می‌شود. اندازه پیشنهادی: ۱۹۲۰×۷۰۰ پیکسل.',
            ),
        ),
        migrations.AddField(
            model_name='aboutpagesettings',
            name='hero_video_url',
            field=models.CharField(
                blank=True,
                max_length=500,
                verbose_name='لینک ویدئو Hero (About Us)',
                help_text='لینک یوتیوب یا هر URL ویدئویی برای پس‌زمینه Hero. اگر هم تصویر و هم لینک وارد شده باشد، تصویر نمایش داده می‌شود.',
            ),
        ),
    ]
