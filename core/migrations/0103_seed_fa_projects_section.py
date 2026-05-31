"""Seed «پروژه‌های ساختمانی آدونیس» section on /fa-new/ homepage.

Creates FaNewSection(section_type='projects', order=10) with 4 default
project cards and a CTA button pointing to /properties/.
Non-destructive: skips if a projects section already exists.
"""
from django.db import migrations


DEFAULT_PROJECTS = [
    {
        'order': 1,
        'title': 'Lotus Residence',
        'location': 'Voula, Athens Riviera',
        'body': 'پروژه لوکس مسکونی با چشم‌انداز دریا در منطقه ساحلی آتن.',
        'badge': 'Luxury Project',
        'cta_label': 'مشاهده پروژه',
        'cta_url': '#fa-section-consult',
    },
    {
        'order': 2,
        'title': 'ERMIS Residence',
        'location': 'Piraeus',
        'body': 'ساختمان بازسازی‌شده مناسب سرمایه‌گذاری و اقامت طلایی یونان.',
        'badge': 'Golden Visa Eligible',
        'cta_label': 'مشاهده پروژه',
        'cta_url': '#fa-section-consult',
    },
    {
        'order': 3,
        'title': 'Onyx Alimos',
        'location': 'Alimos',
        'body': 'پروژه ملکی در جنوب آتن، نزدیک ساحل و مناسب سرمایه‌گذاری.',
        'badge': 'Investment Project',
        'cta_label': 'مشاهده پروژه',
        'cta_url': '#fa-section-consult',
    },
    {
        'order': 4,
        'title': 'Athens Development Project',
        'location': 'Athens',
        'body': 'فرصت منتخب آدونیس برای سرمایه‌گذاری ملکی در مرکز یونان.',
        'badge': 'Featured Property',
        'cta_label': 'مشاهده پروژه',
        'cta_url': '#fa-section-consult',
    },
]


def seed_projects_section(apps, schema_editor):
    FaNewSection = apps.get_model('core', 'FaNewSection')
    FaNewSectionItem = apps.get_model('core', 'FaNewSectionItem')

    if FaNewSection.objects.filter(section_type='projects').exists():
        return

    section = FaNewSection.objects.create(
        section_type='projects',
        order=10,
        is_active=True,
        eyebrow='پروژه‌های آدونیس',
        title='پروژه‌های ساختمانی آدونیس در یونان',
        subtitle='منتخبی از پروژه‌های ملکی و ساختمانی آدونیس برای سرمایه‌گذاری، اقامت طلایی و زندگی در یونان',
    )

    for proj in DEFAULT_PROJECTS:
        FaNewSectionItem.objects.create(
            section=section,
            order=proj['order'],
            title=proj['title'],
            location=proj['location'],
            body=proj['body'],
            badge=proj['badge'],
            cta_label=proj['cta_label'],
            cta_url=proj['cta_url'],
        )


def remove_projects_section(apps, schema_editor):
    FaNewSection = apps.get_model('core', 'FaNewSection')
    FaNewSection.objects.filter(section_type='projects').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0102_fanewsection_services_type_seed'),
    ]

    operations = [
        migrations.RunPython(seed_projects_section, reverse_code=remove_projects_section),
    ]
