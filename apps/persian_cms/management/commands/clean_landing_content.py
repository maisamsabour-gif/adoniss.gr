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
    GVFamilyMember,
    GVDocumentItem,
    GVCostItem,
    GVTestimonial,
    GVFAQItem,
)


def clean_html_content(html):
    """
    Clean HTML content by removing unnecessary inline styles and Word-specific markup.
    """
    if not html:
        return html
    
    original = html
    
    # Remove style attributes from tags
    html = re.sub(r'\s*style\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove class attributes (often Word-specific)
    html = re.sub(r'\s*class\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
    
    # Remove Word-specific tags
    word_tags = ['o:p', 'v:shape', 'v:shapetype', 'w:sdt', 'w:sdtContent', 'w:sdtPr']
    for tag in word_tags:
        html = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(rf'<{tag}[^>]*/>', '', html, flags=re.IGNORECASE)
    
    # Remove empty span tags
    html = re.sub(r'<span\s*>\s*</span>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<span>([^<]*)</span>', r'\1', html, flags=re.IGNORECASE)
    
    # Remove empty paragraphs
    html = re.sub(r'<p\s*>\s*</p>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<p\s*>\s*&nbsp;\s*</p>', '', html, flags=re.IGNORECASE)
    
    # Clean up p tags - keep content, remove attributes
    html = re.sub(r'<p\s+[^>]*>', '<p>', html, flags=re.IGNORECASE)
    
    # Remove font tags (often from Word)
    html = re.sub(r'<font[^>]*>(.*?)</font>', r'\1', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove mso- prefixed styles (Microsoft Office)
    html = re.sub(r'mso-[^;:"\']+[;]?', '', html, flags=re.IGNORECASE)
    
    # Remove XML declarations
    html = re.sub(r'<\?xml[^>]*\?>', '', html, flags=re.IGNORECASE)
    
    # Remove comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove extra whitespace between tags
    html = re.sub(r'>\s+<', '><', html)
    
    # Remove leading/trailing whitespace
    html = html.strip()
    
    # Convert multiple spaces to single space
    html = re.sub(r' +', ' ', html)
    
    # Ensure proper paragraph structure
    # Split by </p> and rejoin with proper spacing
    if '<p>' in html.lower():
        parts = re.split(r'</p>\s*', html, flags=re.IGNORECASE)
        cleaned_parts = []
        for part in parts:
            part = part.strip()
            if part and not part.lower().startswith('<p>'):
                part = '<p>' + part
            if part:
                cleaned_parts.append(part)
        html = '</p>\n'.join(cleaned_parts)
        if cleaned_parts and not html.endswith('</p>'):
            html += '</p>'
    
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
            (GVFamilyMember, ['description']),
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
