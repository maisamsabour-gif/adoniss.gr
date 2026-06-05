"""
Add video_poster field to GVHeroSection.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persian_cms', '0015_benefits_bg_opacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='gvherosection',
            name='video_poster',
            field=models.ImageField(
                blank=True,
                help_text='تصویری که قبل از پخش ویدیو نمایش داده می‌شود',
                upload_to='gv_landing/hero/',
                verbose_name='پوستر ویدیو',
            ),
        ),
    ]
