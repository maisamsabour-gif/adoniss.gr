"""Add why_adonis_stats section type and seed initial data."""
from django.db import migrations, models


def seed_why_adonis_stats(apps, schema_editor):
    """Create the Why Adonis Stats section with 4 cards."""
    FaNewSection = apps.get_model('core', 'FaNewSection')
    FaNewSectionItem = apps.get_model('core', 'FaNewSectionItem')

    # Check if section already exists
    if FaNewSection.objects.filter(section_type='why_adonis_stats').exists():
        return

    # Create the section
    section = FaNewSection.objects.create(
        section_type='why_adonis_stats',
        is_active=True,
        order=1,
        anchor_id='why-adonis',
        eyebrow='چرا آدونیس؟',
        title='اعتماد شما، سرمایه ماست',
        subtitle='بیش از یک دهه تجربه در حوزه اقامت، سرمایه‌گذاری و توسعه پروژه‌های ساختمانی در یونان',
    )

    # Create the 4 stat cards
    cards_data = [
        {
            'order': 1,
            'stat_number': '10',
            'badge': '+',
            'title': 'سال سابقه',
            'body': 'بیش از یک دهه فعالیت تخصصی در حوزه اقامت، سرمایه‌گذاری و املاک یونان',
        },
        {
            'order': 2,
            'stat_number': '450',
            'badge': '+',
            'title': 'خانواده رضایتمند',
            'body': 'همراهی موفق با صدها خانواده در مسیر اخذ اقامت و سرمایه‌گذاری در اروپا',
        },
        {
            'order': 3,
            'stat_number': '250',
            'badge': '+',
            'title': 'پرونده موفق',
            'body': 'تجربه عملی در اجرای پرونده‌های اقامتی و سرمایه‌گذاری با نتایج موفق',
        },
        {
            'order': 4,
            'stat_number': '15',
            'badge': '+',
            'title': 'پروژه اختصاصی آدونیس',
            'body': 'توسعه و مدیریت پروژه‌های ساختمانی اختصاصی در مناطق مختلف یونان',
        },
    ]

    for card_data in cards_data:
        FaNewSectionItem.objects.create(section=section, **card_data)


def reverse_seed(apps, schema_editor):
    """Remove the seeded section."""
    FaNewSection = apps.get_model('core', 'FaNewSection')
    FaNewSection.objects.filter(section_type='why_adonis_stats').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0110_make_menu_url_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fanewsection',
            name='section_type',
            field=models.CharField(
                choices=[
                    ('why_greece', 'مزایای کلیدی یونان'),
                    ('why_adonis', 'آشنایی با آدونیس'),
                    ('why_adonis_stats', 'چرا آدونیس؟ (آمار)'),
                    ('intro_stats', 'آشنایی با آدونیس (قدیمی)'),
                    ('services', 'خدمات آدونیس'),
                    ('routes', 'مسیرهای گلدن ویزا'),
                    ('projects', 'پروژه‌های منتخب'),
                    ('process', 'فرآیند همکاری'),
                    ('trust', 'اعتماد و تجربه'),
                    ('consult', 'مشاوره رایگان'),
                    ('gateway', 'معرفی خدمات آدونیس'),
                    ('residency_types', 'انواع اقامت یونان (۳ کارت لاکچری)'),
                    ('featured_properties', 'پروژه‌های منتخب املاک (کاروسل)'),
                ],
                max_length=20,
                verbose_name='نوع بخش',
            ),
        ),
        migrations.RunPython(seed_why_adonis_stats, reverse_seed),
    ]
