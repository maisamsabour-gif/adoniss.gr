"""
Management command to clean HTML content in Golden Visa Landing Page sections.
Removes unnecessary inline styles, Word-specific tags, and normalizes HTML.

Usage:
    python manage.py clean_landing_content
    python manage.py clean_landing_content --dry-run  # Preview changes without saving
"""

import re
from django.core.management.base import BaseCommand
from django.db import models
from apps.persian_cms.models import (
    GoldenVisaLandingPage,
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
    GVBenefitCard,
    GVEligibilityCard,
    GVProcessStep,
    GVFamilyMemberCard,
    GVDocumentItem,
    GVCostItem,
    GVTestimonial,
    GVFAQItem,
)


def strip_all_html(html):
    """
    Remove ALL HTML tags and return plain text.
    """
    if not html:
        return html
    
    # First unescape HTML entities
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&quot;', '"')
    html = html.replace('&#39;', "'")
    html = html.replace('&amp;', '&')
    html = html.replace('&nbsp;', ' ')
    
    # Remove all HTML tags
    html = re.sub(r'<[^>]+>', '', html)
    
    # Clean up whitespace
    html = re.sub(r'\s+', ' ', html)
    html = html.strip()
    
    # Split into lines for readability (at sentence ends or dashes)
    # Add line breaks after Persian list items
    html = re.sub(r'(\s*-\s+)', r'\n- ', html)
    
    # Clean up multiple newlines
    html = re.sub(r'\n\s*\n', '\n', html)
    html = re.sub(r'^\s*-', '-', html)  # Remove leading space before first dash
    
    return html.strip()


def clean_html_content(html, strip_all_tags=False):
    """
    Clean HTML content by removing unnecessary inline styles and Word-specific markup.
    If strip_all_tags=True, removes ALL HTML and returns plain text.
    """
    if not html:
        return html
    
    # Always strip all tags for this cleanup to get clean content
    return strip_all_html(html)


class Command(BaseCommand):
    help = 'Clean HTML content in Golden Visa Landing Page sections'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be saved'))
        
        total_cleaned = 0
        
        # Models and their text fields to clean
        models_to_clean = [
            (GoldenVisaLandingPage, ['hero_subtitle', 'intro_body', 'benefits_body', 'requirements_body', 'process_body', 'faq_body', 'cta_banner_text', 'meta_description', 'admin_note']),
            (GVHeroSection, ['subtitle', 'description']),
            (GVBenefitsSection, ['section_subtitle', 'section_description']),
            (GVEligibilitySection, ['section_subtitle', 'section_description']),
            (GVProcessSection, ['section_subtitle', 'section_description']),
            (GVStatisticsSection, ['section_subtitle']),
            (GVProjectsSection, ['section_subtitle', 'section_description']),
            (GVFamilySection, ['section_subtitle', 'section_description']),
            (GVDocumentsSection, ['section_subtitle', 'section_description']),
            (GVCostSection, ['section_subtitle', 'section_description']),
            (GVTestimonialsSection, ['section_subtitle', 'section_description']),
            (GVFAQSection, ['section_subtitle']),
            (GVFinalCTASection, ['subtitle', 'description']),
            (GVSEOSettings, ['meta_description', 'og_description', 'schema_json']),
            (GVBenefitCard, ['description']),
            (GVEligibilityCard, ['description']),
            (GVProcessStep, ['description']),
            (GVFamilyMemberCard, ['description']),
            (GVDocumentItem, ['description']),
            (GVCostItem, ['description']),
            (GVTestimonial, ['review_text']),
            (GVFAQItem, ['answer']),
        ]
        
        for model_class, fields in models_to_clean:
            model_name = model_class.__name__
            self.stdout.write(f'\nProcessing {model_name}...')
            
            for obj in model_class.objects.all():
                obj_changed = False
                
                for field_name in fields:
                    if not hasattr(obj, field_name):
                        continue
                    
                    original_value = getattr(obj, field_name)
                    if not original_value:
                        continue
                    
                    cleaned_value = clean_html_content(original_value)
                    
                    if cleaned_value != original_value:
                        self.stdout.write(f'  - {model_name} #{obj.pk}.{field_name}: Cleaning...')
                        
                        if not dry_run:
                            setattr(obj, field_name, cleaned_value)
                            obj_changed = True
                        
                        total_cleaned += 1
                        
                        # Show preview of changes
                        if len(original_value) > 100:
                            self.stdout.write(f'    Before: {original_value[:100]}...')
                            self.stdout.write(f'    After:  {cleaned_value[:100]}...')
                        else:
                            self.stdout.write(f'    Before: {original_value}')
                            self.stdout.write(f'    After:  {cleaned_value}')
                
                if obj_changed and not dry_run:
                    obj.save()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\nDRY RUN: Would clean {total_cleaned} field(s)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully cleaned {total_cleaned} field(s)'))
