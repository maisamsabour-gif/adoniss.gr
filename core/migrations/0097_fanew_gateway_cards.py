from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


def _seed_gateway_cards_from_legacy_fields(apps, schema_editor):
    FaNewSection = apps.get_model('core', 'FaNewSection')
    FaNewGatewayCard = apps.get_model('core', 'FaNewGatewayCard')

    for section in FaNewSection.objects.filter(section_type='gateway').order_by('order', 'id'):
        if FaNewGatewayCard.objects.filter(section_id=section.id).exists():
            continue

        card_specs = [
            {
                'order': 1,
                'badge': section.card_1_label,
                'title': section.card_1_title,
                'subtitle': section.card_1_subtitle,
                'description': section.card_1_description,
                'image': section.card_1_image or section.card_image_1,
                'image_alt': section.card_1_image_alt or section.card_image_1_alt,
                'cta_text': section.card_1_cta_text,
                'cta_link': section.card_1_cta_link,
                'accent_color': section.card_1_accent_color or section.accent_color or '#1E5AA8',
            },
            {
                'order': 2,
                'badge': section.card_2_label,
                'title': section.card_2_title,
                'subtitle': section.card_2_subtitle,
                'description': section.card_2_description,
                'image': section.card_2_image or section.card_image_2,
                'image_alt': section.card_2_image_alt or section.card_image_2_alt,
                'cta_text': section.card_2_cta_text,
                'cta_link': section.card_2_cta_link,
                'accent_color': section.card_2_accent_color or section.accent_color or '#1E5AA8',
            },
        ]

        for spec in card_specs:
            has_content = any([
                spec['badge'],
                spec['title'],
                spec['subtitle'],
                spec['description'],
                spec['image'],
                spec['cta_text'],
                spec['cta_link'],
            ])
            if not has_content:
                continue

            FaNewGatewayCard.objects.create(
                section_id=section.id,
                order=spec['order'],
                is_active=True,
                badge=spec['badge'] or '',
                title=spec['title'] or '',
                subtitle=spec['subtitle'] or '',
                description=spec['description'] or '',
                image=spec['image'],
                image_alt=spec['image_alt'] or '',
                cta_text=spec['cta_text'] or '',
                cta_link=spec['cta_link'] or '',
                overlay_color='transparent',
                overlay_opacity=0,
                accent_color=spec['accent_color'] or '#1E5AA8',
                hover_preset='default',
            )


def _set_gateway_section_defaults(apps, schema_editor):
    FaNewSection = apps.get_model('core', 'FaNewSection')

    for section in FaNewSection.objects.filter(section_type='gateway'):
        changed = []

        if not section.section_name:
            section.section_name = 'بخش مسیرهای سرمایه‌گذاری'
            changed.append('section_name')

        if changed:
            section.save(update_fields=changed)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0096_seo_fields_global_upgrade'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fanewsection',
            options={
                'ordering': ['order'],
                'verbose_name': 'سکشن صفحه اصلی فارسی',
                'verbose_name_plural': 'سکشن‌های صفحه اصلی',
            },
        ),
        migrations.AlterField(
            model_name='fanewsection',
            name='section_type',
            field=models.CharField(
                choices=[
                    ('why_greece', 'چرا یونان؟'),
                    ('why_adonis', 'چرا آدونیس؟'),
                    ('routes', 'مسیرهای گلدن ویزا'),
                    ('projects', 'پروژه‌های منتخب'),
                    ('process', 'فرآیند همکاری'),
                    ('trust', 'اعتماد و تجربه'),
                    ('consult', 'مشاوره رایگان'),
                    ('gateway', 'بخش مسیرهای سرمایه‌گذاری'),
                ],
                max_length=20,
                verbose_name='نوع بخش',
            ),
        ),
        migrations.CreateModel(
            name='FaNewGatewayCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, default=0, help_text='عدد کوچک\u200cتر = نمایش زودتر', verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, help_text='در صورت غیرفعال بودن کارت در فرانت نمایش داده نمی\u200cشود.', verbose_name='فعال')),
                ('badge', models.CharField(blank=True, help_text='مثال: ADONIS DEVELOPMENTS یا GOLDEN VISA', max_length=120, verbose_name='برچسب کارت')),
                ('title', models.CharField(blank=True, max_length=220, verbose_name='عنوان کارت')),
                ('subtitle', models.CharField(blank=True, max_length=260, verbose_name='زیرعنوان کارت')),
                ('description', models.TextField(blank=True, verbose_name='توضیح کارت')),
                ('image', models.ImageField(blank=True, null=True, upload_to='fa-new/sections/cards/', verbose_name='تصویر کارت')),
                ('image_alt', models.CharField(blank=True, max_length=220, verbose_name='alt تصویر کارت')),
                ('cta_text', models.CharField(blank=True, max_length=120, verbose_name='متن CTA')),
                ('cta_link', models.CharField(blank=True, max_length=500, verbose_name='لینک CTA')),
                ('overlay_color', models.CharField(blank=True, default='transparent', help_text='مثال: rgba(11,31,58,0.28) یا #1E5AA8 یا transparent', max_length=30, verbose_name='رنگ overlay کارت')),
                ('overlay_opacity', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='شفافیت overlay (%)')),
                ('accent_color', models.CharField(blank=True, default='#1E5AA8', max_length=30, verbose_name='رنگ accent کارت')),
                ('hover_preset', models.CharField(blank=True, default='default', help_text='رزرو برای استایل hover در نسخه\u200cهای بعدی.', max_length=50, verbose_name='پریست hover (آینده)')),
                (
                    'section',
                    models.ForeignKey(
                        help_text='این کارت فقط برای سکشن «بخش مسیرهای سرمایه\u200cگذاری» استفاده می\u200cشود.',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='gateway_cards',
                        to='core.fanewsection',
                        verbose_name='سکشن',
                    ),
                ),
            ],
            options={
                'verbose_name': 'کارت مسیر سرمایه‌گذاری',
                'verbose_name_plural': 'کارت‌های مسیر سرمایه‌گذاری',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.RunPython(_seed_gateway_cards_from_legacy_fields, migrations.RunPython.noop),
        migrations.RunPython(_set_gateway_section_defaults, migrations.RunPython.noop),
    ]

