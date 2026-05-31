from django.db import migrations, models


SEO_STATUS_CHOICES = [
    ('needs_review', 'Needs review'),
    ('ready', 'Ready'),
    ('critical', 'Critical issues'),
]


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0095_fafooter_logo_max_width'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='Noindex'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='seo_status',
            field=models.CharField(
                choices=SEO_STATUS_CHOICES,
                default='needs_review',
                max_length=20,
                verbose_name='SEO Status',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='meta_title',
            field=models.CharField(blank=True, max_length=100, verbose_name='Meta Title'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='meta_description',
            field=models.CharField(blank=True, max_length=180, verbose_name='Meta Description'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='canonical_url',
            field=models.CharField(blank=True, max_length=300, verbose_name='Canonical URL'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='og_title',
            field=models.CharField(blank=True, max_length=120, verbose_name='OG Title'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='og_description',
            field=models.CharField(blank=True, max_length=220, verbose_name='OG Description'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='og_image',
            field=models.ImageField(blank=True, null=True, upload_to='golden_visa_landing/og/', verbose_name='OG Image'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='focus_keyword',
            field=models.CharField(blank=True, max_length=160, verbose_name='Focus Keyword'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='Noindex'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='seo_status',
            field=models.CharField(
                choices=SEO_STATUS_CHOICES,
                default='needs_review',
                max_length=20,
                verbose_name='SEO Status',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='robots_index',
            field=models.BooleanField(default=True, verbose_name='Robots Index'),
        ),
        migrations.AddField(
            model_name='goldenvisalandingpage',
            name='robots_follow',
            field=models.BooleanField(default=True, verbose_name='Robots Follow'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='canonical_url',
            field=models.CharField(blank=True, max_length=300, verbose_name='Canonical URL'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='og_title',
            field=models.CharField(blank=True, max_length=120, verbose_name='OG Title'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='og_description',
            field=models.CharField(blank=True, max_length=220, verbose_name='OG Description'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='og_image',
            field=models.ImageField(blank=True, null=True, upload_to='golden_visa_fa_landing/og/', verbose_name='OG Image'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='focus_keyword',
            field=models.CharField(blank=True, max_length=160, verbose_name='Focus Keyword'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='Noindex'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='seo_status',
            field=models.CharField(
                choices=SEO_STATUS_CHOICES,
                default='needs_review',
                max_length=20,
                verbose_name='SEO Status',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='robots_index',
            field=models.BooleanField(default=True, verbose_name='Robots Index'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='robots_follow',
            field=models.BooleanField(default=True, verbose_name='Robots Follow'),
        ),
        migrations.AddField(
            model_name='webinarlandingsettings',
            name='canonical_url',
            field=models.CharField(blank=True, default='', max_length=300, verbose_name='Canonical URL'),
        ),
        migrations.AddField(
            model_name='webinarlandingsettings',
            name='og_title',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='OG Title'),
        ),
        migrations.AddField(
            model_name='webinarlandingsettings',
            name='og_description',
            field=models.CharField(blank=True, default='', max_length=220, verbose_name='OG Description'),
        ),
        migrations.AddField(
            model_name='webinarlandingsettings',
            name='og_image',
            field=models.ImageField(blank=True, null=True, upload_to='webinar_landing/og/', verbose_name='OG Image'),
        ),
        migrations.AddField(
            model_name='webinarlandingsettings',
            name='focus_keyword',
            field=models.CharField(blank=True, default='', max_length=160, verbose_name='Focus Keyword'),
        ),
        migrations.AddField(
            model_name='webinarlandingsettings',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='Noindex'),
        ),
        migrations.AddField(
            model_name='webinarlandingsettings',
            name='seo_status',
            field=models.CharField(
                choices=SEO_STATUS_CHOICES,
                default='needs_review',
                max_length=20,
                verbose_name='SEO Status',
            ),
        ),
        migrations.AddField(
            model_name='pageseo',
            name='canonical_url',
            field=models.CharField(blank=True, max_length=300, verbose_name='Canonical URL'),
        ),
        migrations.AddField(
            model_name='pageseo',
            name='focus_keyword',
            field=models.CharField(blank=True, max_length=160, verbose_name='Focus Keyword'),
        ),
        migrations.AddField(
            model_name='pageseo',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='Noindex'),
        ),
        migrations.AddField(
            model_name='pageseo',
            name='seo_status',
            field=models.CharField(
                choices=SEO_STATUS_CHOICES,
                default='needs_review',
                max_length=20,
                verbose_name='SEO Status',
            ),
        ),
        migrations.AddField(
            model_name='pageseo',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
            preserve_default=False,
        ),
    ]
