"""
Add background_opacity field to GVBenefitsSection.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persian_cms', '0014_section_media_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='gvbenefitssection',
            name='background_opacity',
            field=models.CharField(
                default='0.3',
                help_text='عدد بین 0 تا 1 (مثلاً 0.3 یعنی 30% شفافیت)',
                max_length=10,
                verbose_name='شفافیت تصویر پس‌زمینه',
            ),
        ),
    ]
