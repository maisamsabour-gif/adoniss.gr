# Generated manually - Add flat content fields to GoldenVisaLandingPage
from django.db import migrations, models
import django_ckeditor_5.fields


class Migration(migrations.Migration):
    """
    Add flat content sections to GoldenVisaLandingPage.
    These fields allow direct content editing without related models.
    """

    dependencies = [
        ('persian_cms', '0010_gv_landing_page_enhancements'),
    ]

    operations = [
        # Hero Section
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='hero_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='عنوان هیرو'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='hero_subtitle',
            field=models.TextField(blank=True, verbose_name='زیرعنوان هیرو'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='hero_image',
            field=models.ImageField(blank=True, null=True, upload_to='landing/hero/', verbose_name='تصویر هیرو'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='hero_video',
            field=models.FileField(blank=True, null=True, upload_to='landing/videos/', verbose_name='ویدیو هیرو'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='hero_cta_text',
            field=models.CharField(blank=True, max_length=100, verbose_name='متن دکمه CTA'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='hero_cta_link',
            field=models.CharField(blank=True, max_length=200, verbose_name='لینک دکمه CTA'),
        ),
        
        # Intro Section
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='intro_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='عنوان بخش معرفی'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='intro_body',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, verbose_name='متن بخش معرفی'),
        ),
        
        # Benefits Section
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='benefits_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='عنوان بخش مزایا'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='benefits_body',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, verbose_name='محتوای مزایا'),
        ),
        
        # Requirements Section
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='requirements_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='عنوان شرایط'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='requirements_body',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, verbose_name='محتوای شرایط'),
        ),
        
        # Process Section
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='process_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='عنوان مراحل'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='process_body',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, verbose_name='مراحل دریافت ویزا'),
        ),
        
        # FAQ Section
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='faq_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='عنوان سوالات متداول'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='faq_body',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, verbose_name='سوالات متداول'),
        ),
        
        # CTA Banner
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='cta_banner_title',
            field=models.CharField(blank=True, max_length=200, verbose_name='عنوان بنر CTA'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='cta_banner_text',
            field=models.TextField(blank=True, verbose_name='متن بنر CTA'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='cta_banner_button',
            field=models.CharField(blank=True, max_length=100, verbose_name='متن دکمه بنر'),
        ),
        
        # SEO Fields
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='meta_description',
            field=models.TextField(blank=True, verbose_name='توضیحات متا'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='meta_keywords',
            field=models.CharField(blank=True, max_length=500, verbose_name='کلمات کلیدی'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='og_image',
            field=models.ImageField(blank=True, null=True, upload_to='landing/og/', verbose_name='تصویر شبکه اجتماعی'),
        ),
    ]
