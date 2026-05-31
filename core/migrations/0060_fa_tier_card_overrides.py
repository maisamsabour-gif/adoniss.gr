from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_fa_hero_editor_fields'),
    ]

    operations = [
        # Card 1
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_1_title',
            field=models.CharField(blank=True, max_length=220, verbose_name='Tier Card 1 — Title (FA)',
                                   help_text='Persian title for card 1. Leave blank to use auto-translation.'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_1_short_desc',
            field=models.CharField(blank=True, max_length=320, verbose_name='Tier Card 1 — Short Description (FA)',
                                   help_text='1-2 line description shown on the card face.'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_1_long_desc',
            field=models.TextField(blank=True, verbose_name='Tier Card 1 — Long Description (FA)',
                                   help_text='Full description shown in the expandable panel.'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_1_price_label',
            field=models.CharField(blank=True, max_length=80, verbose_name='Tier Card 1 — Price Label (FA)',
                                   help_text='e.g. شروع از'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_1_price_amount',
            field=models.CharField(blank=True, max_length=80, verbose_name='Tier Card 1 — Price Amount',
                                   help_text='e.g. €250,000'),
        ),
        # Card 2
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_2_title',
            field=models.CharField(blank=True, max_length=220, verbose_name='Tier Card 2 — Title (FA)',
                                   help_text='Persian title for card 2. Leave blank to use auto-translation.'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_2_short_desc',
            field=models.CharField(blank=True, max_length=320, verbose_name='Tier Card 2 — Short Description (FA)'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_2_long_desc',
            field=models.TextField(blank=True, verbose_name='Tier Card 2 — Long Description (FA)'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_2_price_label',
            field=models.CharField(blank=True, max_length=80, verbose_name='Tier Card 2 — Price Label (FA)'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_2_price_amount',
            field=models.CharField(blank=True, max_length=80, verbose_name='Tier Card 2 — Price Amount'),
        ),
        # Card 3
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_3_title',
            field=models.CharField(blank=True, max_length=220, verbose_name='Tier Card 3 — Title (FA)',
                                   help_text='Persian title for card 3. Leave blank to use auto-translation.'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_3_short_desc',
            field=models.CharField(blank=True, max_length=320, verbose_name='Tier Card 3 — Short Description (FA)'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_3_long_desc',
            field=models.TextField(blank=True, verbose_name='Tier Card 3 — Long Description (FA)'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_3_price_label',
            field=models.CharField(blank=True, max_length=80, verbose_name='Tier Card 3 — Price Label (FA)'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='tier_3_price_amount',
            field=models.CharField(blank=True, max_length=80, verbose_name='Tier Card 3 — Price Amount'),
        ),
    ]
