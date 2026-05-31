from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_create_property_blog_manager_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoldenVisaLandingPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero_title', models.CharField(default='Greek Golden Visa', max_length=200, verbose_name='Hero Title')),
                ('hero_subtitle', models.TextField(default='Secure EU permanent residency for your family through strategic property investment in Greece.', verbose_name='Hero Subtitle')),
                ('intro_text', models.TextField(blank=True, help_text='Rich introductory paragraph shown below the hero.', verbose_name='Intro / About Text')),
                ('tier_250_title', models.CharField(default='Commercial-to-Residential Converted Properties', max_length=200, verbose_name='€250K Tier Title')),
                ('tier_250_desc', models.TextField(default='Invest in converted commercial-to-residential properties across Greece starting from €250,000.', verbose_name='€250K Tier Description')),
                ('tier_250_image', models.ImageField(blank=True, help_text='Landscape image (min 1200×600 px)', null=True, upload_to='golden_visa_landing/', verbose_name='€250K Tier Image')),
                ('tier_400_title', models.CharField(default='Other Greek Regions', max_length=200, verbose_name='€400K Tier Title')),
                ('tier_400_desc', models.TextField(default='Invest in properties across other Greek regions starting from €400,000.', verbose_name='€400K Tier Description')),
                ('tier_400_image', models.ImageField(blank=True, null=True, upload_to='golden_visa_landing/', verbose_name='€400K Tier Image')),
                ('tier_800_title', models.CharField(default='Premium Locations', max_length=200, verbose_name='€800K Tier Title')),
                ('tier_800_desc', models.TextField(default='Invest in premium locations such as Athens, Thessaloniki, Mykonos, and Santorini starting from €800,000.', verbose_name='€800K Tier Description')),
                ('tier_800_image', models.ImageField(blank=True, null=True, upload_to='golden_visa_landing/', verbose_name='€800K Tier Image')),
                ('benefits_title', models.CharField(default='Why Choose the Greek Golden Visa?', max_length=200, verbose_name='Benefits Section Title')),
                ('benefits_text', models.TextField(blank=True, default='EU Permanent Residency\nVisa-Free Travel in Schengen Zone\nIncludes Spouse & Dependent Children\nNo Minimum Stay Requirement\nPath to Greek Citizenship after 7 Years\nStrong ROI on Greek Real Estate\nAccess to EU Healthcare & Education\nFast Processing — Typically 2–3 Months', help_text='Enter each benefit on its own line. They will be displayed as a grid of cards.', verbose_name='Benefits (one per line)')),
                ('process_title', models.CharField(default='How It Works', max_length=200, verbose_name='Process Section Title')),
                ('process_steps', models.TextField(blank=True, default='Choose Your Investment Tier\nSelect a Qualifying Property with Adonis\nComplete Legal Due Diligence\nSign Purchase Agreement & Transfer Funds\nSubmit Golden Visa Application\nReceive Residency Permit (5-Year Renewable)', help_text='Each line becomes a numbered step card.', verbose_name='Process Steps (one per line)')),
                ('youtube_urls', models.TextField(blank=True, help_text='Paste one YouTube URL per line (watch or youtu.be format).', verbose_name='YouTube Video URLs')),
                ('faq', models.TextField(blank=True, help_text='Optional. Enter as JSON array: [{"q": "Question?", "a": "Answer."}, ...]', verbose_name='FAQ (JSON)')),
                ('seo_title', models.CharField(blank=True, help_text='Leave blank to use Hero Title. Max 70 chars.', max_length=70, verbose_name='SEO Title')),
                ('meta_description', models.CharField(blank=True, help_text='Max 160 chars. Used by Google & social previews.', max_length=160, verbose_name='Meta Description')),
                ('og_image', models.ImageField(blank=True, help_text='Recommended: 1200×630 px.', null=True, upload_to='golden_visa_landing/', verbose_name='OG / Social Share Image')),
                ('is_published', models.BooleanField(default=True, help_text='Uncheck to show a "Coming Soon" placeholder instead.', verbose_name='Published')),
            ],
            options={
                'verbose_name': 'Golden Visa Landing Page',
                'verbose_name_plural': 'Golden Visa Landing Page',
            },
        ),
    ]
