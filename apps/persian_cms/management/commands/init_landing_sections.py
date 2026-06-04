"""
Management command to initialize all sections for existing landing pages.
Run this once to create missing section objects.

Usage:
    python manage.py init_landing_sections
"""

from django.core.management.base import BaseCommand
from apps.persian_cms.models import GoldenVisaLandingPage


class Command(BaseCommand):
    help = 'Initialize all sections for existing Golden Visa Landing Pages'

    def handle(self, *args, **options):
        from apps.persian_cms.models import (
            GVHeroSection,
            GVBenefitsSection,
            GVEligibilitySection,
            GVProcessSection,
            GVStatisticsSection,
            GVProjectsSection,
            GVFamilySection,
            GVDocumentsSection,
            GVCostSection,
            GVTestimonialsSection,
            GVFAQSection,
            GVFinalCTASection,
            GVSEOSettings,
            GVAnimationSettings,
            GVDesignSettings,
        )
        
        landing_pages = GoldenVisaLandingPage.objects.all()
        
        if not landing_pages.exists():
            self.stdout.write(self.style.WARNING('No landing pages found.'))
            return
        
        for lp in landing_pages:
            self.stdout.write(f'\nProcessing: {lp.title} (ID: {lp.pk})')
            
            sections_config = [
                (GVHeroSection, {
                    'main_title': lp.hero_title or 'گلدن ویزای یونان',
                    'highlighted_word': 'یونان',
                    'subtitle': lp.hero_subtitle or 'اقامت اروپا با خرید ملک',
                    'display_order': 1,
                }),
                (GVBenefitsSection, {
                    'section_title': 'مزایای اقامت دائم یونان',
                    'section_subtitle': 'چرا هزاران سرمایه‌گذار، یونان را انتخاب می‌کنند؟',
                    'display_order': 2,
                }),
                (GVEligibilitySection, {
                    'section_title': 'شرایط سرمایه‌گذاری',
                    'section_subtitle': 'سه مسیر سرمایه‌گذاری متناسب با بودجه شما',
                    'display_order': 3,
                }),
                (GVProcessSection, {
                    'section_title': 'مراحل دریافت اقامت',
                    'section_subtitle': 'از مشاوره تا دریافت کارت اقامت',
                    'display_order': 4,
                }),
                (GVStatisticsSection, {
                    'section_title': 'آمار و ارقام',
                    'section_subtitle': 'عملکرد ما در یک نگاه',
                    'display_order': 5,
                }),
                (GVProjectsSection, {
                    'section_title': 'پروژه‌های ساختمانی',
                    'section_subtitle': 'پروژه‌های واجد شرایط گلدن ویزا',
                    'display_order': 6,
                }),
                (GVFamilySection, {
                    'section_title': 'اقامت خانوادگی',
                    'section_subtitle': 'اقامت برای تمام اعضای خانواده',
                    'display_order': 7,
                }),
                (GVDocumentsSection, {
                    'section_title': 'مدارک مورد نیاز',
                    'section_subtitle': 'لیست مدارک لازم برای ثبت درخواست',
                    'display_order': 8,
                }),
                (GVCostSection, {
                    'section_title': 'هزینه‌ها',
                    'section_subtitle': 'تمام هزینه‌ها به صورت شفاف',
                    'display_order': 9,
                }),
                (GVTestimonialsSection, {
                    'section_title': 'نظرات مشتریان',
                    'section_subtitle': 'تجربه واقعی مشتریان آدونیس',
                    'display_order': 10,
                }),
                (GVFAQSection, {
                    'section_title': 'سوالات متداول',
                    'section_subtitle': 'پاسخ به سوالات رایج',
                    'display_order': 11,
                }),
                (GVFinalCTASection, {
                    'title': 'همین حالا اقدام کنید',
                    'subtitle': 'تیم متخصص ما آماده پاسخگویی است',
                    'display_order': 12,
                }),
                (GVSEOSettings, {
                    'seo_title': lp.title,
                    'meta_description': lp.meta_description or f'{lp.title} - اقامت اروپا با سرمایه‌گذاری',
                }),
                (GVAnimationSettings, {
                    'animations_enabled': True,
                }),
                (GVDesignSettings, {
                    'primary_color': '#D4AF37',
                    'secondary_color': '#1a1a2e',
                }),
            ]
            
            created_count = 0
            for model_class, defaults in sections_config:
                obj, created = model_class.objects.get_or_create(
                    landing_page=lp,
                    defaults=defaults
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✓ Created: {model_class.__name__}')
                else:
                    self.stdout.write(f'  - Exists: {model_class.__name__}')
            
            self.stdout.write(self.style.SUCCESS(f'  Total created: {created_count}'))
        
        self.stdout.write(self.style.SUCCESS('\nDone!'))
