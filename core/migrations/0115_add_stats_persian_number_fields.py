# Generated manually for adding why_adonis_stats customization fields

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0114_add_hero_position_and_font_sizes'),
    ]

    operations = [
        migrations.AddField(
            model_name='fanewsection',
            name='stats_use_persian_numbers',
            field=models.BooleanField(
                default=True,
                verbose_name='اعداد فارسی',
                help_text='اعداد آماری را به صورت فارسی (۰۱۲۳۴۵۶۷۸۹) نمایش بده',
            ),
        ),
        migrations.AddField(
            model_name='fanewsection',
            name='stats_number_font_size',
            field=models.PositiveIntegerField(
                default=56,
                validators=[MinValueValidator(20), MaxValueValidator(120)],
                verbose_name='سایز عدد (px)',
                help_text='سایز فونت اعداد آماری در دسکتاپ. پیشنهاد: ۴۸ تا ۷۲ پیکسل',
            ),
        ),
        migrations.AddField(
            model_name='fanewsection',
            name='stats_number_font_size_mobile',
            field=models.PositiveIntegerField(
                default=40,
                validators=[MinValueValidator(16), MaxValueValidator(80)],
                verbose_name='سایز عدد موبایل (px)',
                help_text='سایز فونت اعداد آماری در موبایل. پیشنهاد: ۳۲ تا ۴۸ پیکسل',
            ),
        ),
        migrations.AddField(
            model_name='fanewsection',
            name='stats_number_color',
            field=models.CharField(
                max_length=30,
                blank=True,
                default='#D4B057',
                verbose_name='رنگ اعداد',
                help_text='رنگ اعداد آماری. پیش‌فرض: طلایی (#D4B057)',
            ),
        ),
        migrations.AddField(
            model_name='fanewsection',
            name='stats_suffix_font_size',
            field=models.PositiveIntegerField(
                default=32,
                validators=[MinValueValidator(12), MaxValueValidator(60)],
                verbose_name='سایز پسوند (+)',
                help_text='سایز فونت پسوند (مثل +) در دسکتاپ',
            ),
        ),
        migrations.AddField(
            model_name='fanewsection',
            name='stats_card_title_font_size',
            field=models.PositiveIntegerField(
                default=16,
                validators=[MinValueValidator(12), MaxValueValidator(32)],
                verbose_name='سایز عنوان کارت',
                help_text='سایز فونت عنوان زیر هر عدد (مثلاً «سال سابقه»)',
            ),
        ),
        migrations.AddField(
            model_name='fanewsection',
            name='stats_animation_duration',
            field=models.PositiveIntegerField(
                default=2000,
                validators=[MinValueValidator(500), MaxValueValidator(5000)],
                verbose_name='مدت انیمیشن (ms)',
                help_text='مدت زمان انیمیشن شمارش اعداد به میلی‌ثانیه',
            ),
        ),
    ]
