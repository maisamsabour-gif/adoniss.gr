"""
Data migration: copy existing English content from the base columns into the
new modeltranslation _en columns for GoldenVisaLandingPage.

This runs once after 0048_gv_landing_translation adds the _en / _tr columns.
After this migration the singleton page will have all English text in the
correct _en columns so the admin and frontend display correctly.
"""
from django.db import migrations

_TEXT_FIELDS = [
    'hero_title',
    'hero_subtitle',
    'intro_text',
    'section_1_title',
    'section_1_text',
    'section_2_title',
    'section_2_text',
    'section_3_title',
    'section_3_text',
    'tier_250_title',
    'tier_250_desc',
    'tier_400_title',
    'tier_400_desc',
    'tier_800_title',
    'tier_800_desc',
    'benefits_title',
    'benefits_text',
    'process_title',
    'process_steps',
]


def copy_to_en(apps, schema_editor):
    """
    1. Copy base-field value → _en column (if _en is still empty).
    2. Clear _tr columns that are identical to the English default — this happens
       because modeltranslation auto-fills _tr with the same field default.  We
       want _tr to be empty so the auto-translate actions can fill them correctly.
    """
    GoldenVisaLandingPage = apps.get_model('core', 'GoldenVisaLandingPage')
    for obj in GoldenVisaLandingPage.objects.all():
        for field in _TEXT_FIELDS:
            en_field = f'{field}_en'
            tr_field = f'{field}_tr'
            base_val  = (getattr(obj, field,    '') or '').strip()
            en_val    = (getattr(obj, en_field, '') or '').strip()
            tr_val    = (getattr(obj, tr_field, '') or '').strip()

            # Ensure EN column has the real English content
            if base_val and not en_val:
                setattr(obj, en_field, base_val)
                en_val = base_val  # refresh for comparison below

            # Clear TR column if it still contains the same text as EN
            # (migration default filled it with the English string)
            if tr_val and tr_val == en_val:
                setattr(obj, tr_field, '')

        obj.save()


def reverse_copy(apps, schema_editor):
    pass  # Reversing is a no-op; _en columns will just be left populated


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_gv_landing_translation'),
    ]

    operations = [
        migrations.RunPython(copy_to_en, reverse_copy),
    ]
