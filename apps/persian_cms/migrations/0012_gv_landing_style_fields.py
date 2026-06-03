# Generated manually - Add style fields to GoldenVisaLandingPage

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persian_cms', '0011_gv_landing_flat_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_font_family',
            field=models.CharField(
                choices=[
                    ('Vazirmatn', 'وزیرمتن'),
                    ('IRANSans', 'ایران سنس'),
                    ('Yekan', 'یکان'),
                    ('Samim', 'صمیم'),
                    ('Shabnam', 'شبنم'),
                    ('Tahoma', 'تاهوما'),
                ],
                default='Vazirmatn',
                max_length=50,
                verbose_name='فونت اصلی',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_primary_color',
            field=models.CharField(
                default='#c9a227',
                help_text='رنگ دکمه‌ها و آیکون‌ها - مثال: #c9a227',
                max_length=20,
                verbose_name='رنگ اصلی (طلایی)',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_secondary_color',
            field=models.CharField(
                default='#0a1530',
                help_text='رنگ پس‌زمینه هیرو و سکشن‌ها - مثال: #0a1530',
                max_length=20,
                verbose_name='رنگ ثانویه (تیره)',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_hero_title_size',
            field=models.CharField(
                default='3.5rem',
                help_text='مثال: 3rem, 3.5rem, 4rem',
                max_length=20,
                verbose_name='سایز عنوان هیرو',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_section_title_size',
            field=models.CharField(
                default='2.4rem',
                help_text='مثال: 2rem, 2.4rem, 2.8rem',
                max_length=20,
                verbose_name='سایز عنوان سکشن‌ها',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_body_text_size',
            field=models.CharField(
                default='1.1rem',
                help_text='مثال: 1rem, 1.1rem, 1.2rem',
                max_length=20,
                verbose_name='سایز متن بدنه',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_button_radius',
            field=models.CharField(
                default='14px',
                help_text='مثال: 8px, 12px, 14px, 50px',
                max_length=20,
                verbose_name='گردی دکمه‌ها',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_card_radius',
            field=models.CharField(
                default='20px',
                help_text='مثال: 12px, 16px, 20px, 24px',
                max_length=20,
                verbose_name='گردی کارت‌ها',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='style_hero_overlay_opacity',
            field=models.CharField(
                default='0.85',
                help_text='عدد بین 0 تا 1 - مثال: 0.7, 0.85, 0.9',
                max_length=10,
                verbose_name='شفافیت overlay هیرو',
            ),
        ),
    ]
