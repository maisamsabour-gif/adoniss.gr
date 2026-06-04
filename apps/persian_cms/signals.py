"""
Signals for Persian CMS app.
Auto-creates all section objects when a Golden Visa Landing Page is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='persian_cms.GoldenVisaLandingPage')
def create_landing_page_sections(sender, instance, created, **kwargs):
    """
    Auto-create all section objects when a new landing page is created.
    Each section gets default Persian titles that admin can customize.
    """
    from .models import (
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
    
    # Define sections with their default titles
    sections_config = [
        (GVHeroSection, {
            'main_title': 'گلدن ویزای یونان',
            'highlighted_word': 'یونان',
            'subtitle': 'اقامت اروپا با خرید ملک',
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
            'seo_title': instance.title,
            'meta_description': f'{instance.title} - اقامت اروپا با سرمایه‌گذاری در یونان',
        }),
        (GVAnimationSettings, {
            'animations_enabled': True,
        }),
        (GVDesignSettings, {
            'primary_color': '#D4AF37',
            'secondary_color': '#1a1a2e',
        }),
    ]
    
    for model_class, defaults in sections_config:
        model_class.objects.get_or_create(
            landing_page=instance,
            defaults=defaults
        )
