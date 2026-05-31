"""
Data migration: normalise FaNewSection data so the admin panel reflects the
intended front-page layout:

  0  —  why_greece   →  مزایای کلیدی یونان   (benefits cards, rendered after Hero)
  1  —  why_adonis   →  آشنایی با آدونیس     (was intro_stats in old codebase)
  2  —  gateway      →  معرفی خدمات آدونیس   (investment-route cards)

Steps performed:
  1. Convert any section whose section_type is 'intro_stats' to 'why_adonis'.
  2. Re-number the three canonical sections to orders 0, 1, 2 so the admin
     list shows them in the same sequence as the rendered page.
"""

from django.db import migrations


def _fix_sections(apps, schema_editor):
    FaNewSection = apps.get_model('core', 'FaNewSection')

    # 1. Promote legacy intro_stats → why_adonis
    FaNewSection.objects.filter(section_type='intro_stats').update(
        section_type='why_adonis',
    )

    # 2. Re-assign canonical orders so admin list mirrors page layout
    order_map = {
        'why_greece': 0,
        'why_adonis': 1,
        'gateway':    2,
    }
    for section_type, order in order_map.items():
        FaNewSection.objects.filter(section_type=section_type).update(order=order)


def _reverse_fix(apps, schema_editor):
    """Reverse is a best-effort only — restores intro_stats type but not exact orders."""
    FaNewSection = apps.get_model('core', 'FaNewSection')
    FaNewSection.objects.filter(section_type='why_adonis').update(
        section_type='intro_stats',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_fanew_gateway_cards'),
    ]

    operations = [
        migrations.RunPython(_fix_sections, reverse_code=_reverse_fix),
    ]
