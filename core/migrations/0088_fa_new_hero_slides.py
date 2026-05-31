from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0087_fa_new_sections'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaNewHeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('settings', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='hero_slides',
                    to='core.fanewsettings',
                    verbose_name='تنظیمات',
                )),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب')),
                ('eyebrow', models.CharField(
                    blank=True, max_length=100,
                    help_text='مثال: ADONIS · ATHENS  یا  خانه · آتن',
                    verbose_name='متن کوچک بالای عنوان',
                )),
                ('headline', models.CharField(
                    max_length=250,
                    help_text='متن کامل عنوان. کلمه‌ای که می‌خواهی طلایی شود را در فیلد بعدی بنویس.',
                    verbose_name='عنوان اصلی',
                )),
                ('headline_highlight', models.CharField(
                    blank=True, max_length=100,
                    help_text='این کلمه با رنگ طلایی نشان داده می‌شود. باید دقیقاً با متن عنوان یکسان باشد.',
                    verbose_name='کلمه طلایی در عنوان',
                )),
                ('subtitle', models.CharField(
                    blank=True, max_length=250,
                    help_text='متن کوچک‌تر زیر عنوان اصلی. برای اسلاید آخر (CTA) خالی بگذارید.',
                    verbose_name='زیرعنوان',
                )),
                ('is_cta', models.BooleanField(
                    default=False,
                    help_text='فعال کن اگر این اسلاید آخر است و دو دکمه دارد.',
                    verbose_name='اسلاید CTA (دکمه‌دار)؟',
                )),
                ('cta_primary_label', models.CharField(
                    blank=True, default='دریافت مشاوره', max_length=80,
                    verbose_name='متن دکمه اول',
                )),
                ('cta_primary_url', models.CharField(
                    blank=True, default='#fa-section-consult', max_length=300,
                    verbose_name='لینک دکمه اول',
                )),
                ('cta_secondary_label', models.CharField(
                    blank=True, default='مشاهده پروژه‌ها', max_length=80,
                    verbose_name='متن دکمه دوم',
                )),
                ('cta_secondary_url', models.CharField(
                    blank=True, default='#fa-section-projects', max_length=300,
                    verbose_name='لینک دکمه دوم',
                )),
                ('start_time', models.FloatField(
                    default=0.0,
                    help_text='زمان شروع نمایش این اسلاید در انیمیشن اسکرول (مقیاس ۰ تا ۱۰)',
                    verbose_name='شروع (scroll scale 0–10)',
                )),
                ('end_time', models.FloatField(
                    default=3.0,
                    verbose_name='پایان (scroll scale 0–10)',
                )),
            ],
            options={
                'verbose_name': 'اسلاید هیرو',
                'verbose_name_plural': 'اسلایدهای هیرو',
                'ordering': ['order'],
            },
        ),
    ]
