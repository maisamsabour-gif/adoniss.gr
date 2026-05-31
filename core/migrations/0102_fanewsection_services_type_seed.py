"""Add 'services' to FaNewSection.section_type choices and seed default data.

Creates the «خدمات آدونیس» section with 4 service cards right after the
benefits section (why_greece) in the /fa-new/ homepage.
"""
from django.db import migrations, models


DEFAULT_CARDS = [
    {
        'order': 1,
        'title': 'اقامت طلایی یونان با خرید ملک',
        'body': 'دریافت اقامت یونان از طریق خرید ملک واجد شرایط، همراه با انتخاب ملک، امور حقوقی و پیگیری کامل پرونده.',
        'badge': 'tall',
        'cta_label': 'مشاهده جزئیات',
        'cta_url': '#fa-section-consult',
    },
    {
        'order': 2,
        'title': 'اقامت تمکن مالی یونان',
        'body': 'مناسب برای افرادی که درآمد پایدار خارج از یونان دارند و می‌خواهند اقامت قانونی اروپا را دریافت کنند.',
        'badge': '',
        'cta_label': 'مشاهده جزئیات',
        'cta_url': '#fa-section-consult',
    },
    {
        'order': 3,
        'title': 'افتتاح حساب بانکی',
        'body': 'همراهی در آماده‌سازی مدارک، هماهنگی با بانک و پیگیری مراحل افتتاح حساب در یونان.',
        'badge': '',
        'cta_label': 'مشاهده جزئیات',
        'cta_url': '#fa-section-consult',
    },
    {
        'order': 4,
        'title': 'سرمایه‌گذاری در یونان',
        'body': 'مشاوره تخصصی برای انتخاب فرصت‌های مطمئن سرمایه‌گذاری در املاک، کسب‌وکار و پروژه‌های توسعه‌ای.',
        'badge': 'tall',
        'cta_label': 'مشاهده جزئیات',
        'cta_url': '#fa-section-consult',
    },
]


def seed_services_section(apps, schema_editor):
    FaNewSection = apps.get_model('core', 'FaNewSection')
    FaNewSectionItem = apps.get_model('core', 'FaNewSectionItem')

    # Idempotent: only create if no services section exists yet
    if FaNewSection.objects.filter(section_type='services').exists():
        return

    section = FaNewSection.objects.create(
        section_type='services',
        order=5,
        is_active=True,
        eyebrow='خدمات ما',
        title='خدمات آدونیس',
        subtitle='راهکارهای تخصصی آدونیس برای اقامت، سرمایه‌گذاری و شروع زندگی در یونان',
    )

    for card_data in DEFAULT_CARDS:
        FaNewSectionItem.objects.create(
            section=section,
            order=card_data['order'],
            title=card_data['title'],
            body=card_data['body'],
            badge=card_data['badge'],
            cta_label=card_data['cta_label'],
            cta_url=card_data['cta_url'],
        )


def remove_services_section(apps, schema_editor):
    FaNewSection = apps.get_model('core', 'FaNewSection')
    FaNewSection.objects.filter(section_type='services').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0100_fanewsection_background_image_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fanewsection',
            name='section_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('gateway', 'معرفی خدمات آدونیس'),
                    ('intro_stats', 'آشنایی با آدونیس (قدیمی)'),
                    ('why_adonis', 'آشنایی با آدونیس'),
                    ('why_greece', 'مزایای کلیدی یونان'),
                    ('services', 'خدمات آدونیس'),
                    ('routes', 'مسیرهای گلدن ویزا'),
                    ('projects', 'پروژه‌های منتخب'),
                    ('process', 'فرآیند همکاری'),
                    ('trust', 'اعتماد و تجربه'),
                    ('consult', 'مشاوره رایگان'),
                ],
                verbose_name='نوع بخش',
            ),
        ),
        migrations.RunPython(seed_services_section, reverse_code=remove_services_section),
    ]
