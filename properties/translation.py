"""
django-modeltranslation options for the properties app.

Translatable fields on Property:
  - name / slug           → property title and URL slug per language
  - tagline               → short card description
  - description           → full HTML description
  - location              → address / area text
  - neighborhood_description
  - feature_1 … feature_4 → badge highlights shown on the card
  - area_highlight_1 … area_highlight_6
"""

from modeltranslation.translator import register, TranslationOptions

from .models import Property, PropertyMedia


@register(Property)
class PropertyTranslationOptions(TranslationOptions):
    fields = (
        'name',
        'slug',
        'tagline',
        'description',
        'location',
        'area',
        'neighborhood_public',
        'neighborhood_description',
        'feature_1',
        'feature_2',
        'feature_3',
        'feature_4',
        'area_highlight_1',
        'area_highlight_2',
        'area_highlight_3',
        'area_highlight_4',
        'area_highlight_5',
        'area_highlight_6',
    )
    # English name + slug are required; all Turkish fields are optional with fallback
    required_languages = {'en': ('name', 'slug')}


@register(PropertyMedia)
class PropertyMediaTranslationOptions(TranslationOptions):
    """Per-language ALT text for each gallery image."""
    fields = ('caption',)
