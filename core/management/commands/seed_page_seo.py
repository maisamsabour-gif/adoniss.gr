"""
Seed default EN/TR PageSEO entries for the main pages.
Safe to re-run — only fills blank fields, never overwrites existing content.

Usage:
    python manage.py seed_page_seo
    python manage.py seed_page_seo --overwrite   # reset ALL to defaults
"""

from django.core.management.base import BaseCommand
from core.models import PageSEO


# NOTE: Do NOT include the brand name in meta_title_* values.
# base.html automatically appends "| Adonis Group" to every title.
DEFAULTS = [
    {
        'page_key': 'home',
        'meta_title_en': 'Greece Golden Visa & Property Investment',
        'meta_desc_en': (
            'Discover how to obtain the Greece Golden Visa through property investment. '
            'Learn about requirements, benefits, and available real estate opportunities.'
        ),
        'og_title_en': 'Greece Golden Visa Experts — Adonis Group',
        'og_desc_en': (
            'Official partner for Greece Golden Visa. Explore premium Athens properties '
            'and secure EU residency for your family with Adonis Group.'
        ),
        'meta_title_tr': 'Yunanistan Altın Vize & Gayrimenkul Yatırımı',
        'meta_desc_tr': (
            'Yunanistan Altın Vize\'sini gayrimenkul yatırımı yoluyla nasıl edineceğinizi keşfedin. '
            'Şartlar, avantajlar ve mevcut emlak fırsatları hakkında bilgi alın.'
        ),
        'og_title_tr': 'Yunanistan Altın Vize Uzmanları — Adonis Group',
        'og_desc_tr': (
            'Yunanistan Altın Vize\'si için resmi ortak. Atina\'nın en iyi mülklerini keşfederek '
            'aileniz için AB oturma iznini Adonis Group ile güvence altına alın.'
        ),
    },
    {
        'page_key': 'properties',
        'meta_title_en': 'Golden Visa Properties in Greece',
        'meta_desc_en': (
            'Discover premium Greece Golden Visa investment opportunities through real estate. '
            'Explore exclusive properties in Athens and secure European residency with Adonis.'
        ),
        'og_title_en': 'Invest in Greece — Golden Visa Properties',
        'og_desc_en': (
            'Browse handpicked Athens and Greek island properties starting from €250K. '
            'Qualify for the Greece Golden Visa and gain EU permanent residency.'
        ),
        'meta_title_tr': 'Yunanistan\'da Altın Vize Mülkleri',
        'meta_desc_tr': (
            'Yunanistan\'da Altın Vize için premium gayrimenkul yatırım fırsatlarını keşfedin. '
            'Atina\'daki özel mülkleri inceleyin ve Adonis ile Avrupa oturma iznini elde edin.'
        ),
        'og_title_tr': 'Yunanistan\'a Yatırım — Altın Vize Mülkleri',
        'og_desc_tr': (
            '250.000 €\'dan başlayan fiyatlarla seçkin Atina ve Yunan adası mülklerini görüntüleyin. '
            'Yunanistan Altın Vize\'sine hak kazanın ve AB kalıcı oturma iznini edinin.'
        ),
    },
    {
        'page_key': 'golden_visa',
        'meta_title_en': 'Greek Golden Visa Programme — Investment Guide',
        'meta_desc_en': (
            'Everything you need to know about the Greek Golden Visa. '
            'Investment tiers, benefits, process steps, and how Adonis Group guides you every step of the way.'
        ),
        'og_title_en': 'Greek Golden Visa — Full Guide & Investment Tiers',
        'og_desc_en': (
            'Explore €250K, €400K and €800K investment tiers for the Greece Golden Visa. '
            'EU permanent residency, visa-free Schengen travel, and strong real estate ROI.'
        ),
        'meta_title_tr': 'Yunan Altın Vize Programı — Yatırım Rehberi',
        'meta_desc_tr': (
            'Yunanistan Altın Vize hakkında bilmeniz gereken her şey. '
            'Yatırım seviyeleri, avantajlar, süreç adımları ve Adonis Group\'un adım adım rehberliği.'
        ),
        'og_title_tr': 'Yunan Altın Vize — Tam Rehber ve Yatırım Seviyeleri',
        'og_desc_tr': (
            'Yunanistan Altın Vize için 250.000 €, 400.000 € ve 800.000 € yatırım seviyelerini keşfedin. '
            'AB kalıcı oturma izni, vizesiz Schengen seyahati ve güçlü gayrimenkul getirisi.'
        ),
    },
    {
        'page_key': 'blog',
        'meta_title_en': 'Golden Visa & Greece Real Estate Insights',
        'meta_desc_en': (
            'Expert articles on Greece Golden Visa requirements, real estate market updates, '
            'investment tips, and residency guides from the Adonis Group team.'
        ),
        'meta_title_tr': 'Altın Vize & Yunan Gayrimenkul Rehberi',
        'meta_desc_tr': (
            'Yunanistan Altın Vize gereksinimleri, gayrimenkul piyasası güncellemeleri, '
            'yatırım ipuçları ve oturma izni rehberleri hakkında uzman makaleler.'
        ),
    },
    {
        'page_key': 'contact',
        'meta_title_en': 'Contact Us — Free Golden Visa Consultation',
        'meta_desc_en': (
            'Get in touch with Adonis Group for a free Golden Visa consultation. '
            'Offices in Athens. Multilingual team ready to assist you.'
        ),
        'meta_title_tr': 'İletişim — Ücretsiz Altın Vize Danışmanlığı',
        'meta_desc_tr': (
            'Ücretsiz Altın Vize danışmanlığı için Adonis Group ile iletişime geçin. '
            'Atina ofisimizde çok dilli ekibimiz size yardımcı olmaya hazır.'
        ),
    },
    {
        'page_key': 'about',
        'meta_title_en': 'About Us — Greek Golden Visa Experts',
        'meta_desc_en': (
            'Learn about Adonis Group — our mission, team, and track record helping '
            'international investors obtain Greek Golden Visa residency permits.'
        ),
        'meta_title_tr': 'Hakkımızda — Yunan Altın Vize Uzmanları',
        'meta_desc_tr': (
            'Adonis Group hakkında bilgi edinin — misyonumuz, ekibimiz ve uluslararası yatırımcılara '
            'Yunanistan Altın Vize oturma izni edinmelerinde sağladığımız destek.'
        ),
    },
    {
        'page_key': 'partnerships',
        'meta_title_en': 'Partner With Us — Golden Visa Real Estate Referrals',
        'meta_desc_en': (
            'Join the Adonis Group partner network. Earn competitive commissions by referring '
            'clients to Greece Golden Visa real estate investment opportunities.'
        ),
        'meta_title_tr': 'İş Ortaklığı — Altın Vize Gayrimenkul Referansları',
        'meta_desc_tr': (
            'Adonis Group ortak ağına katılın. Müşterileri Yunanistan Altın Vize gayrimenkul '
            'yatırım fırsatlarına yönlendirerek rekabetçi komisyonlar kazanın.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Seed default EN/TR PageSEO entries. Safe to re-run (blank fields only).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite ALL fields, even ones with existing content.',
        )

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        created = updated = skipped = 0

        for data in DEFAULTS:
            key = data['page_key']
            obj, is_new = PageSEO.objects.get_or_create(page_key=key)

            if is_new:
                for field, value in data.items():
                    if field != 'page_key':
                        setattr(obj, field, value)
                obj.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  Created PageSEO: {key}'))
            else:
                changed = False
                for field, value in data.items():
                    if field == 'page_key':
                        continue
                    if overwrite or not getattr(obj, field, ''):
                        setattr(obj, field, value)
                        changed = True
                if changed:
                    obj.save()
                    updated += 1
                    self.stdout.write(f'  Updated PageSEO: {key}')
                else:
                    skipped += 1
                    self.stdout.write(f'  Skipped (already complete): {key}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done — created: {created}, updated: {updated}, skipped: {skipped}.'
        ))
