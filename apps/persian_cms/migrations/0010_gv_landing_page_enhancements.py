# Generated manually - NON-DESTRUCTIVE migration for Golden Visa Landing Page enhancements
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Non-destructive migration that adds:
    1. admin_note field to GoldenVisaLandingPage
    2. hero_image_alt field to GVHeroSection
    3. GVFaPropertyRelation model for linking FaProperty to landing page
    
    This migration does NOT delete any existing data or models.
    """

    dependencies = [
        ('persian_cms', '0009_golden_visa_landing_page'),
    ]

    operations = [
        # 1. Add admin_note field to GoldenVisaLandingPage
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='admin_note',
            field=models.TextField(
                blank=True,
                verbose_name='یادداشت ادمین',
                help_text='توضیح کوتاه داخلی برای مدیران (در سایت نمایش داده نمی‌شود)',
            ),
        ),
        
        # 2. Add hero_image_alt field to GVHeroSection
        migrations.AddField(
            model_name='gvherosection',
            name='hero_image_alt',
            field=models.CharField(
                max_length=200,
                blank=True,
                verbose_name='Alt Text تصویر هیرو',
                help_text='توضیح تصویر برای سئو و دسترسی‌پذیری',
            ),
        ),
        
        # 3. Create GVFaPropertyRelation model
        migrations.CreateModel(
            name='GVFaPropertyRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='بروزرسانی')),
                ('display_title', models.CharField(
                    blank=True,
                    max_length=200,
                    verbose_name='عنوان نمایشی',
                    help_text='عنوان جایگزین برای نمایش در لندینگ (اختیاری)',
                )),
                ('display_description', models.TextField(
                    blank=True,
                    verbose_name='توضیح نمایشی',
                    help_text='توضیح کوتاه جایگزین (اختیاری)',
                )),
                ('badge_text', models.CharField(
                    blank=True,
                    default='مناسب گلدن ویزا',
                    max_length=100,
                    verbose_name='متن نشان',
                    help_text='مثلاً: مناسب گلدن ویزا، پیشنهاد ویژه',
                )),
                ('display_order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
                ('projects_section', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='property_relations',
                    to='persian_cms.gvprojectssection',
                    verbose_name='بخش پروژه‌ها',
                )),
                ('property', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='gv_landing_relations',
                    to='persian_cms.faproperty',
                    verbose_name='پروژه ملکی',
                    help_text='پروژه را از لیست پروژه‌های ملکی فارسی انتخاب کنید',
                )),
            ],
            options={
                'db_table': 'gv_fa_property_relation',
                'verbose_name': 'پروژه مرتبط (از FaProperty)',
                'verbose_name_plural': 'پروژه‌های مرتبط (از FaProperty)',
                'ordering': ['display_order', 'pk'],
                'unique_together': {('projects_section', 'property')},
            },
        ),
    ]
