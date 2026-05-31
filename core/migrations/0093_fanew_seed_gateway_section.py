from django.db import migrations
from django.db.models import Max


def _seed_gateway_section(apps, schema_editor):
    FaNewSection = apps.get_model('core', 'FaNewSection')

    gateways = FaNewSection.objects.filter(section_type='gateway').order_by('id')
    if gateways.exists():
        # Safe backfill for older rows without touching custom user content.
        for section in gateways:
            changed = []
            if not section.section_name:
                section.section_name = 'Gateway دو کارتی'
                changed.append('section_name')
            if not section.anchor_id:
                section.anchor_id = 'fa-section-gateway'
                changed.append('anchor_id')
            if not section.title:
                section.title = 'مسیر مناسب خودتان را انتخاب کنید'
                changed.append('title')
            if not section.subtitle:
                section.subtitle = 'دو مسیر شخصی‌سازی‌شده برای شرایط متفاوت'
                changed.append('subtitle')
            if not section.description:
                section.description = 'این سکشن از پنل ادمین کاملا مدیریت می‌شود.'
                changed.append('description')
            if not section.card_1_title and not section.card_2_title:
                section.card_1_label = section.card_1_label or 'مسیر استاندارد'
                section.card_1_title = section.card_1_title or 'شروع از ۲۵۰ هزار یورو'
                section.card_1_subtitle = section.card_1_subtitle or 'مناسب سرمایه‌گذاران محتاط'
                section.card_1_description = section.card_1_description or 'بررسی پرونده، انتخاب ملک و پشتیبانی اقامت.'
                section.card_1_cta_text = section.card_1_cta_text or 'جزئیات مسیر اول'
                section.card_1_cta_link = section.card_1_cta_link or '#fa-section-consult'
                section.card_2_label = section.card_2_label or 'مسیر پرایم'
                section.card_2_title = section.card_2_title or 'سرمایه‌گذاری مناطق ویژه'
                section.card_2_subtitle = section.card_2_subtitle or 'گزینه سریع‌تر برای خانواده'
                section.card_2_description = section.card_2_description or 'انتخاب مناطق پربازده با تحلیل دقیق تیم آدونیس.'
                section.card_2_cta_text = section.card_2_cta_text or 'جزئیات مسیر دوم'
                section.card_2_cta_link = section.card_2_cta_link or '#fa-section-consult'
                changed.extend([
                    'card_1_label', 'card_1_title', 'card_1_subtitle', 'card_1_description',
                    'card_1_cta_text', 'card_1_cta_link',
                    'card_2_label', 'card_2_title', 'card_2_subtitle', 'card_2_description',
                    'card_2_cta_text', 'card_2_cta_link',
                ])
            if changed:
                section.save(update_fields=changed)
        return

    max_order = FaNewSection.objects.aggregate(max_order=Max('order')).get('max_order') or 0
    FaNewSection.objects.create(
        section_name='Gateway دو کارتی',
        section_type='gateway',
        is_active=True,
        order=max_order + 1,
        anchor_id='fa-section-gateway',
        show_on_desktop=True,
        show_on_mobile=True,
        title='مسیر مناسب خودتان را انتخاب کنید',
        subtitle='دو مسیر شخصی‌سازی‌شده برای شرایط متفاوت',
        description='این سکشن از پنل ادمین کاملا مدیریت می‌شود.',
        cta_primary_text='دریافت مشاوره رایگان',
        cta_primary_url='#fa-section-consult',
        cta_secondary_text='مشاهده پروژه‌ها',
        cta_secondary_url='#fa-section-projects',
        card_1_label='مسیر استاندارد',
        card_1_title='شروع از ۲۵۰ هزار یورو',
        card_1_subtitle='مناسب سرمایه‌گذاران محتاط',
        card_1_description='بررسی پرونده، انتخاب ملک و پشتیبانی اقامت.',
        card_1_cta_text='جزئیات مسیر اول',
        card_1_cta_link='#fa-section-consult',
        card_2_label='مسیر پرایم',
        card_2_title='سرمایه‌گذاری مناطق ویژه',
        card_2_subtitle='گزینه سریع‌تر برای خانواده',
        card_2_description='انتخاب مناطق پربازده با تحلیل دقیق تیم آدونیس.',
        card_2_cta_text='جزئیات مسیر دوم',
        card_2_cta_link='#fa-section-consult',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0092_fanew_section_management_fields'),
    ]

    operations = [
        migrations.RunPython(_seed_gateway_section, migrations.RunPython.noop),
    ]
