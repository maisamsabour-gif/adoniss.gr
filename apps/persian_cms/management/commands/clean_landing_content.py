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


def clean_html_content(html, strip_all_tags=False):
    """
    Clean HTML content by removing unnecessary inline styles and Word-specific markup.
    If strip_all_tags=True, removes ALL HTML and returns plain text.
    """
    if not html:
        return html
    
    original = html
    
    # First, unescape any HTML entities that represent tags
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&quot;', '"')
    html = html.replace('&#39;', "'")
    html = html.replace('&amp;', '&')
    
    # Remove ALL style attributes
    html = re.sub(r'\s*style\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove ALL class attributes
    html = re.sub(r'\s*class\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove ALL id attributes
    html = re.sub(r'\s*id\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove ALL data- attributes
    html = re.sub(r'\s*data-[a-z0-9-]+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove Word-specific tags completely
    word_tags = ['o:p', 'v:shape', 'v:shapetype', 'w:sdt', 'w:sdtContent', 'w:sdtPr', 'xml', 'meta', 'link', 'style']
    for tag in word_tags:
        html = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(rf'<{tag}[^>]*/>', '', html, flags=re.IGNORECASE)
        html = re.sub(rf'<{tag}[^>]*>', '', html, flags=re.IGNORECASE)
    
    # Remove span tags completely but keep content
    html = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove div tags but keep content  
    html = re.sub(r'<div[^>]*>(.*?)</div>', r'\1', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove font tags but keep content
    html = re.sub(r'<font[^>]*>(.*?)</font>', r'\1', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean p tags - remove all attributes
    html = re.sub(r'<p\s+[^>]*>', '<p>', html, flags=re.IGNORECASE)
    
    # Clean other common tags
    for tag in ['strong', 'b', 'i', 'em', 'u', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br']:
        # Keep tag but remove attributes (except href for <a>)
        if tag == 'a':
            # For links, keep href but remove other attributes
            html = re.sub(rf'<a\s+(?:(?!href)[^>])*href\s*=\s*["\']([^"\']*)["\'][^>]*>', r'<a href="\1">', html, flags=re.IGNORECASE)
        else:
            html = re.sub(rf'<{tag}\s+[^>]*>', f'<{tag}>', html, flags=re.IGNORECASE)
    
    # Remove empty tags
    html = re.sub(r'<p>\s*</p>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<p>\s*&nbsp;\s*</p>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<p>&nbsp;</p>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<br\s*/?>\s*<br\s*/?>', '<br>', html, flags=re.IGNORECASE)
    
    # Remove XML/DOCTYPE declarations
    html = re.sub(r'<\?xml[^>]*\?>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)
    
    # Remove HTML comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove mso- prefixed anything
    html = re.sub(r'mso-[^;:"\'>\s]+[;]?', '', html, flags=re.IGNORECASE)
    
    # Clean up multiple newlines
    html = re.sub(r'\n\s*\n', '\n', html)
    
    # Clean up extra whitespace
    html = re.sub(r' +', ' ', html)
    html = re.sub(r'>\s+<', '><', html)
    
    # Remove &nbsp; at start/end of paragraphs
    html = re.sub(r'<p>&nbsp;', '<p>', html, flags=re.IGNORECASE)
    html = re.sub(r'&nbsp;</p>', '</p>', html, flags=re.IGNORECASE)
    
    # Strip leading/trailing whitespace
    html = html.strip()
    
    # If strip_all_tags requested, remove everything
    if strip_all_tags:
        html = re.sub(r'<[^>]+>', '', html)
        html = re.sub(r'&nbsp;', ' ', html)
        html = re.sub(r' +', ' ', html)
        html = html.strip()
    
    return html


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
