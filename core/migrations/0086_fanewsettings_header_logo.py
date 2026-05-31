from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_fa_new_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='fanewsettings',
            name='header_logo',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='fa-new/',
                verbose_name='لوگو هدر (Header Logo)',
                help_text=(
                    'لوگوی نمایش داده شده در هدر صفحه /fa-new/ . '
                    'فرمت PNG با پس‌زمینه شفاف پیشنهاد می‌شود. '
                    'ارتفاع ۶۰–۱۲۰ پیکسل ایده‌آل است.'
                ),
            ),
        ),
    ]
