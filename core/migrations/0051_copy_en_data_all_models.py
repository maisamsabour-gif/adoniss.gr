"""
Data migration: copy existing base field values to _en columns and clear any
_tr columns that got auto-populated with the same English text.
"""
from django.db import migrations


_MODELS_AND_FIELDS = {
    ('core', 'AboutPageSettings'): [
        'hero_title', 'hero_subtitle', 'about_title', 'about_text',
        'team_title', 'team_subtitle',
    ],
    ('core', 'PropertiesPageSettings'): [
        'hero_title', 'hero_subtitle', 'hero_badge', 'intro_title', 'intro_text',
    ],
    ('core', 'TeamMember'): ['position', 'bio'],
    ('core', 'Office'): ['city', 'country', 'address'],
    # ALT fields newly added to existing translated models
    ('core', 'BlogPost'): ['featured_image_alt'],
    ('core', 'GoldenVisaCard'): ['image_alt'],
    ('core', 'Event'): ['thumbnail_alt'],
    ('core', 'Testimonial'): ['image_alt'],
    ('core', 'GoldenVisaLandingPage'): [
        'hero_image_alt',
        'section_1_image_alt', 'section_2_image_alt', 'section_3_image_alt',
        'tier_250_image_alt', 'tier_400_image_alt', 'tier_800_image_alt',
    ],
}


def copy_to_en(apps, schema_editor):
    for (app, model_name), fields in _MODELS_AND_FIELDS.items():
        Model = apps.get_model(app, model_name)
        for obj in Model.objects.all():
            for field in fields:
                en_f = f'{field}_en'
                tr_f = f'{field}_tr'
                base_val = (getattr(obj, field, '') or '').strip()
                en_val = (getattr(obj, en_f, '') or '').strip()
                tr_val = (getattr(obj, tr_f, '') or '').strip()

                if base_val and not en_val:
                    setattr(obj, en_f, base_val)
                    en_val = base_val

                if tr_val and tr_val == en_val:
                    setattr(obj, tr_f, '')
            obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0050_add_tr_fields_all_models'),
    ]
    operations = [
        migrations.RunPython(copy_to_en, migrations.RunPython.noop),
    ]
