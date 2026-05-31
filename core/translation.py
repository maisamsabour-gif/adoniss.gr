"""
django-modeltranslation options for core content models.

Registers which fields on each model get English + Turkish variants.
Convention: modeltranslation automatically creates  <field>_en  and  <field>_tr
columns and maps  obj.<field>  to the active language column at runtime.

Fallback rule: if the Turkish field is empty, the English value is returned
(configured in settings via MODELTRANSLATION_FALLBACK_LANGUAGES or per-model).
"""

from modeltranslation.translator import register, TranslationOptions

from .models import (
    AboutPageSettings,
    BlogCategory,
    BlogPost,
    Event,
    FAQ,
    FooterSettings,
    FrontPageSettings,
    GoldenVisaCard,
    GoldenVisaLandingPage,
    HeaderSettings,
    Office,
    PartnershipPageSettings,
    PropertiesPageSettings,
    Service,
    TeamMember,
    Testimonial,
)


@register(BlogPost)
class BlogPostTranslationOptions(TranslationOptions):
    fields = (
        'title',
        'slug',
        'excerpt',
        'content',
        'featured_image_alt',
        'meta_title',
        'meta_description',
        'og_title',
        'og_description',
    )
    required_languages = {'en': ('title', 'slug', 'excerpt', 'content')}


@register(BlogCategory)
class BlogCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')


@register(GoldenVisaCard)
class GoldenVisaCardTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'description', 'image_alt')


@register(Event)
class EventTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'short_description', 'full_description', 'thumbnail_alt')
    required_languages = {'en': ('title', 'slug')}


@register(Testimonial)
class TestimonialTranslationOptions(TranslationOptions):
    fields = ('content', 'image_alt')


@register(FooterSettings)
class FooterSettingsTranslationOptions(TranslationOptions):
    fields = ('description', 'whatsapp_button_text')


@register(HeaderSettings)
class HeaderSettingsTranslationOptions(TranslationOptions):
    fields = (
        'hero_title', 'hero_subtitle',
        'intro_title', 'intro_text',
        'contact_button_text',
    )


@register(FrontPageSettings)
class FrontPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        'services_badge', 'services_title', 'services_description',
        'process_badge', 'process_title', 'process_description',
        'catalogue_badge_text', 'catalogue_heading', 'catalogue_subtext',
        'catalogue_btn1_title', 'catalogue_btn1_label',
        'catalogue_btn2_title', 'catalogue_btn2_label',
        'contact_badge', 'contact_title', 'contact_description',
    )


@register(GoldenVisaLandingPage)
class GoldenVisaLandingPageTranslationOptions(TranslationOptions):
    """
    Registers all user-visible text fields on the Greece Golden Visa landing page
    for English + Turkish translation.  SEO/OG/Twitter fields are NOT translated
    here (they stay English-only for search engine consistency); the page-level
    SEO is handled by PageSEO which already has per-language records.
    """
    fields = (
        'hero_title',
        'hero_subtitle',
        'hero_image_alt',
        'intro_text',
        'section_1_title',
        'section_1_text',
        'section_1_image_alt',
        'section_2_title',
        'section_2_text',
        'section_2_image_alt',
        'section_3_title',
        'section_3_text',
        'section_3_image_alt',
        'tier_250_title',
        'tier_250_desc',
        'tier_250_image_alt',
        'tier_400_title',
        'tier_400_desc',
        'tier_400_image_alt',
        'tier_800_title',
        'tier_800_desc',
        'tier_800_image_alt',
        'benefits_title',
        'benefits_text',
        'process_title',
        'process_steps',
    )


@register(PartnershipPageSettings)
class PartnershipPageSettingsTranslationOptions(TranslationOptions):
    fields = (
        'hero_title', 'hero_subtitle',
        'video_title', 'video_subtitle',
        'b2b_title', 'b2b_text',
        'benefit_1_title', 'benefit_1_text',
        'benefit_2_title', 'benefit_2_text',
        'benefit_3_title', 'benefit_3_text',
        'benefit_4_title', 'benefit_4_text',
        'benefit_5_title', 'benefit_5_text',
        'benefit_6_title', 'benefit_6_text',
        'cta_title', 'cta_text', 'cta_button_text',
    )


@register(AboutPageSettings)
class AboutPageSettingsTranslationOptions(TranslationOptions):
    fields = ('hero_title', 'hero_subtitle', 'about_title', 'about_text', 'team_title', 'team_subtitle')


@register(PropertiesPageSettings)
class PropertiesPageSettingsTranslationOptions(TranslationOptions):
    fields = ('hero_title', 'hero_subtitle', 'hero_badge', 'intro_title', 'intro_text')


@register(TeamMember)
class TeamMemberTranslationOptions(TranslationOptions):
    fields = ('position', 'bio')


@register(Office)
class OfficeTranslationOptions(TranslationOptions):
    fields = ('city', 'country', 'address')
