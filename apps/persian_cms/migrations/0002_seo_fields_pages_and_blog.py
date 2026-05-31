from django.db import migrations, models


SEO_STATUS_CHOICES = [
    ('needs_review', 'Needs review'),
    ('ready', 'Ready'),
    ('critical', 'Critical issues'),
]


class Migration(migrations.Migration):
    dependencies = [
        ('persian_cms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='persianpage',
            name='meta_title',
            field=models.CharField(blank=True, max_length=260, verbose_name='Meta Title'),
        ),
        migrations.AddField(
            model_name='persianpage',
            name='meta_description',
            field=models.TextField(blank=True, verbose_name='Meta Description'),
        ),
        migrations.AddField(
            model_name='persianpage',
            name='canonical_url',
            field=models.URLField(blank=True, verbose_name='Canonical URL'),
        ),
        migrations.AddField(
            model_name='persianpage',
            name='og_title',
            field=models.CharField(blank=True, max_length=260, verbose_name='OG Title'),
        ),
        migrations.AddField(
            model_name='persianpage',
            name='og_description',
            field=models.TextField(blank=True, verbose_name='OG Description'),
        ),
        migrations.AddField(
            model_name='persianpage',
            name='og_image',
            field=models.ImageField(blank=True, null=True, upload_to='persian_cms/og/', verbose_name='OG Image'),
        ),
        migrations.AddField(
            model_name='persianpage',
            name='focus_keyword',
            field=models.CharField(blank=True, max_length=180, verbose_name='Focus Keyword'),
        ),
        migrations.AddField(
            model_name='persianpage',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='Noindex'),
        ),
        migrations.AddField(
            model_name='persianpage',
            name='seo_status',
            field=models.CharField(
                choices=SEO_STATUS_CHOICES,
                default='needs_review',
                max_length=20,
                verbose_name='SEO Status',
            ),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='meta_title',
            field=models.CharField(blank=True, max_length=260, verbose_name='Meta Title'),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='meta_description',
            field=models.TextField(blank=True, verbose_name='Meta Description'),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='canonical_url',
            field=models.URLField(blank=True, verbose_name='Canonical URL'),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='og_title',
            field=models.CharField(blank=True, max_length=260, verbose_name='OG Title'),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='og_description',
            field=models.TextField(blank=True, verbose_name='OG Description'),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='og_image',
            field=models.ImageField(blank=True, null=True, upload_to='persian_cms/blog/og/', verbose_name='OG Image'),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='focus_keyword',
            field=models.CharField(blank=True, max_length=180, verbose_name='Focus Keyword'),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='Noindex'),
        ),
        migrations.AddField(
            model_name='persianblogpost',
            name='seo_status',
            field=models.CharField(
                choices=SEO_STATUS_CHOICES,
                default='needs_review',
                max_length=20,
                verbose_name='SEO Status',
            ),
        ),
        migrations.AddField(
            model_name='persianseosettings',
            name='focus_keyword',
            field=models.CharField(blank=True, max_length=180, verbose_name='Focus Keyword'),
        ),
        migrations.AddField(
            model_name='persianseosettings',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='Noindex'),
        ),
        migrations.AddField(
            model_name='persianseosettings',
            name='seo_status',
            field=models.CharField(
                choices=SEO_STATUS_CHOICES,
                default='needs_review',
                max_length=20,
                verbose_name='SEO Status',
            ),
        ),
    ]
