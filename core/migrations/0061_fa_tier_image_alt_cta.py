from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0060_fa_tier_card_overrides')]

    operations = [
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_1_image',
            field=models.ImageField(blank=True, null=True, upload_to='golden_visa_fa_landing/tiers/'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_1_image_alt',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_1_cta_text',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_2_image',
            field=models.ImageField(blank=True, null=True, upload_to='golden_visa_fa_landing/tiers/'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_2_image_alt',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_2_cta_text',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_3_image',
            field=models.ImageField(blank=True, null=True, upload_to='golden_visa_fa_landing/tiers/'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_3_image_alt',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_3_cta_text',
            field=models.CharField(blank=True, max_length=80),
        ),
    ]
