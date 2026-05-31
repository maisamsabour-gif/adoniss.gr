from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0089_fanewsettings_overlay_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='FaNewSettings',
            name='hero_label',
            field=models.CharField(
                blank=True, max_length=100,
                verbose_name='لیبل طلایی بالای عنوان',
                help_text='متن کوچک طلایی که بالای عنوان اصلی نشان داده می‌شود. مثال: ADONIS · ATHENS',
            ),
        ),
        migrations.AddField(
            model_name='FaNewSettings',
            name='hero_title',
            field=models.CharField(
                blank=True, max_length=200,
                verbose_name='عنوان اصلی هیرو',
                help_text='عنوان بزرگ که روی ویدیو نمایش داده می‌شود.',
            ),
        ),
        migrations.AddField(
            model_name='FaNewSettings',
            name='hero_subtitle',
            field=models.CharField(
                blank=True, max_length=300,
                verbose_name='زیرعنوان هیرو',
                help_text='متن کوچک‌تر زیر عنوان اصلی.',
            ),
        ),
        migrations.AddField(
            model_name='FaNewSettings',
            name='hero_cta_text',
            field=models.CharField(
                blank=True, max_length=100,
                verbose_name='متن دکمه CTA',
                help_text='متن دکمه اصلی روی هیرو. مثال: دریافت مشاوره رایگان',
            ),
        ),
        migrations.AddField(
            model_name='FaNewSettings',
            name='hero_cta_url',
            field=models.CharField(
                blank=True, max_length=200,
                verbose_name='لینک دکمه CTA',
                help_text='آدرس لینک دکمه. مثال: #fa-section-consult',
            ),
        ),
    ]
