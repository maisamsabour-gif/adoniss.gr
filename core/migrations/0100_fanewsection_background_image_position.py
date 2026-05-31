from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0099_fanewsection_background_image_opacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='fanewsection',
            name='background_image_position',
            field=models.CharField(
                blank=True,
                choices=[
                    ('center center', 'مرکز وسط (پیش‌فرض)'),
                    ('center top', 'بالا - مرکز'),
                    ('center bottom', 'پایین - مرکز'),
                    ('right center', 'مرکز - راست'),
                    ('left center', 'مرکز - چپ'),
                ],
                default='center center',
                max_length=30,
                verbose_name='موقعیت تصویر پس‌زمینه',
                help_text='کنترل می‌کند کدام بخش از تصویر در مرکز نمایش باشد. برای تصاویر عمودی «بالا - مرکز» مناسب است.',
            ),
        ),
    ]
