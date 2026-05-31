from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [('core', '0055_sitesettings_google_ads_fields')]

    operations = [
        migrations.CreateModel(
            name='GoldenVisaFaLandingPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero_title', models.CharField(default='Greek Golden Visa', max_length=220)),
                ('hero_subtitle', models.TextField(blank=True)),
                ('hero_cta_text', models.CharField(default='Get Free Consultation', max_length=120)),
                ('hero_image', models.ImageField(blank=True, null=True, upload_to='golden_visa_fa_landing/')),
                ('hero_image_alt', models.CharField(blank=True, max_length=200)),
                ('hero_video', models.FileField(blank=True, null=True, upload_to='golden_visa_fa_landing/')),
                ('intro_title', models.CharField(blank=True, max_length=220)),
                ('intro_text', models.TextField(blank=True)),
                ('intro_image', models.ImageField(blank=True, null=True, upload_to='golden_visa_fa_landing/')),
                ('intro_image_alt', models.CharField(blank=True, max_length=200)),
                ('tiers_title', models.CharField(blank=True, max_length=220)),
                ('projects_title', models.CharField(blank=True, max_length=220)),
                ('benefits_title', models.CharField(blank=True, max_length=220)),
                ('benefits_bg_image', models.ImageField(blank=True, null=True, upload_to='golden_visa_fa_landing/')),
                ('benefits_text', models.TextField(blank=True)),
                ('process_title', models.CharField(blank=True, max_length=220)),
                ('process_steps', models.TextField(blank=True)),
                ('own_shorts_title', models.CharField(blank=True, max_length=220)),
                ('own_short_video_url_1', models.CharField(blank=True, max_length=500)),
                ('own_short_video_url_2', models.CharField(blank=True, max_length=500)),
                ('own_short_video_url_3', models.CharField(blank=True, max_length=500)),
                ('own_short_video_url_4', models.CharField(blank=True, max_length=500)),
                ('testimonial_shorts_title', models.CharField(blank=True, max_length=220)),
                ('testimonial_short_video_url_1', models.CharField(blank=True, max_length=500)),
                ('testimonial_short_video_url_2', models.CharField(blank=True, max_length=500)),
                ('testimonial_short_video_url_3', models.CharField(blank=True, max_length=500)),
                ('testimonial_short_video_url_4', models.CharField(blank=True, max_length=500)),
                ('seo_title', models.CharField(blank=True, max_length=100)),
                ('meta_description', models.CharField(blank=True, max_length=180)),
                ('is_published', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Persian Golden Visa Landing Page (FA)',
                'verbose_name_plural': 'Persian Golden Visa Landing Page (FA)',
            },
        ),
    ]
