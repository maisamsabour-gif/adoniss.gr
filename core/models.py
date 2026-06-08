"""
core/models.py  — Adonis site data models.
Reconstructed from compiled bytecode + database schema.
"""
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from ckeditor.fields import RichTextField
from django_ckeditor_5.fields import CKEditor5Field

from core.safety import SoftDeleteModel
from core.seo_mixin import SEOContentInterface

SEO_STATUS_CHOICES = [
    ('needs_review', 'Needs review'),
    ('ready', 'Ready'),
    ('critical', 'Critical issues'),
]


# ── Singleton base ─────────────────────────────────────────────────────────────

class _SingletonMixin(models.Model):
    """Ensure only one row exists; use get_or_create in views."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ── SiteSettings ──────────────────────────────────────────────────────────────

class SiteSettings(_SingletonMixin):
    """Global site settings"""
    site_name = models.CharField(max_length=100, default='Adonis Group', verbose_name='Site Name')
    tagline = models.CharField(max_length=200, default='Greek Residency & Immigration', verbose_name='Tagline')
    hero_title = models.CharField(max_length=200, default='Greek Residency', verbose_name='Hero Title')
    hero_subtitle = models.TextField(default='Permanent residency for your family by purchasing property in Greece', verbose_name='Hero Subtitle')
    whatsapp_number = models.CharField(max_length=100, default='+306985989596', verbose_name='WhatsApp Number')
    phone_number = models.CharField(max_length=20, default='+30 210 7000 570', verbose_name='Phone')
    email = models.EmailField(default='info@adonisgroup.gr', verbose_name='Email')
    address = models.TextField(default='Athens, Alimos, Poseidonos Avenue, No. 78, 1st Floor', verbose_name='Address')
    instagram_url = models.URLField(max_length=200, blank=True, verbose_name='Instagram URL')
    facebook_url = models.URLField(max_length=200, blank=True, verbose_name='Facebook URL')
    linkedin_url = models.URLField(max_length=200, blank=True, verbose_name='LinkedIn URL')
    telegram_bot_token = models.CharField(max_length=100, blank=True, verbose_name='Telegram Bot Token')
    telegram_chat_id = models.CharField(max_length=100, blank=True, verbose_name='Telegram Chat ID')
    telegram_enabled = models.BooleanField(default=False, verbose_name='Enable Telegram Notifications')
    meta_description = models.TextField(blank=True, verbose_name='Meta Description')
    meta_keywords = models.CharField(max_length=300, blank=True, verbose_name='Meta Keywords')
    google_analytics_id = models.CharField(max_length=50, blank=True, verbose_name='Google Analytics ID')
    google_ads_conversion_id = models.CharField(max_length=50, blank=True, verbose_name='Google Ads Conversion ID')
    google_ads_conversion_label = models.CharField(max_length=120, blank=True, verbose_name='Google Ads Conversion Label')
    microsoft_clarity_id = models.CharField(max_length=50, blank=True, verbose_name='Microsoft Clarity ID')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'


# ── HeaderSettings ────────────────────────────────────────────────────────────

OVERLAY_CHOICES = [('dark', 'Dark'), ('light', 'Light'), ('none', 'None')]
FILTER_CHOICES = [('none', 'None'), ('blur', 'Blur'), ('grayscale', 'Grayscale')]


class HeaderSettings(_SingletonMixin):
    """Header / Navigation settings"""
    site_name = models.CharField(max_length=100, default='Adonis Group', verbose_name='Site Name')
    logo = models.ImageField(upload_to='header/', blank=True, null=True, verbose_name='Logo')
    logo_width = models.PositiveIntegerField(default=160, verbose_name='Logo Width (px)')
    logo_height = models.PositiveIntegerField(default=50, verbose_name='Logo Height (px)')
    hero_video = models.FileField(upload_to='hero/', blank=True, null=True, verbose_name='Hero Video (File)')
    hero_video_url = models.CharField(max_length=500, blank=True, verbose_name='Hero Video (YouTube URL)')
    hero_video_poster = models.ImageField(upload_to='hero/', blank=True, null=True, verbose_name='Video Poster / Fallback Image')
    hero_video_embed_url = models.URLField(max_length=500, blank=True, verbose_name='Hero Video Embed URL')
    hero_title = models.CharField(max_length=200, default='Greek Residency', verbose_name='Hero Title')
    hero_subtitle = models.TextField(default='Permanent residency for your family by purchasing property in Greece | Official offices in Athens', verbose_name='Hero Subtitle')
    hero_overlay = models.CharField(max_length=20, default='dark', choices=OVERLAY_CHOICES, verbose_name='Video Overlay')
    hero_overlay_opacity = models.PositiveIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Overlay Opacity (%)')
    hero_filter = models.CharField(max_length=20, default='none', choices=FILTER_CHOICES, verbose_name='Video Filter')
    hero_brightness = models.PositiveIntegerField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)], verbose_name='Video Brightness (%)')
    whatsapp_number = models.CharField(max_length=100, blank=True, verbose_name='WhatsApp Number')
    contact_button_text = models.CharField(max_length=50, default='Contact', verbose_name='Contact Button Text')
    show_home = models.BooleanField(default=True, verbose_name='Show Home')
    show_properties = models.BooleanField(default=True, verbose_name='Show Properties')
    show_partnerships = models.BooleanField(default=True, verbose_name='Show Partnerships')
    show_about = models.BooleanField(default=True, verbose_name='Show About')
    show_contact = models.BooleanField(default=True, verbose_name='Show Contact')
    intro_video = models.FileField(upload_to='header/', blank=True, null=True, verbose_name='Intro Video (File)')
    intro_video_url = models.CharField(max_length=500, blank=True, verbose_name='Intro Video URL')
    intro_video_poster = models.ImageField(upload_to='header/', blank=True, null=True, verbose_name='Intro Video Poster')
    intro_video_embed_url = models.URLField(max_length=500, blank=True, verbose_name='Intro Video Embed URL')
    intro_title = models.CharField(max_length=200, blank=True, verbose_name='Intro Title')
    intro_text = models.TextField(blank=True, verbose_name='Intro Text')

    class Meta:
        verbose_name = 'Header Settings'
        verbose_name_plural = 'Header Settings'

    def __str__(self):
        return 'Header Settings'

    @property
    def intro_video_embed(self):
        """
        Return a YouTube embed URL with autoplay enabled, suitable for an
        iframe. Accepts any of these formats from either ``intro_video_embed_url``
        or ``intro_video_url``:
            - https://youtu.be/VIDEO_ID
            - https://www.youtube.com/watch?v=VIDEO_ID
            - https://www.youtube.com/embed/VIDEO_ID
            - https://www.youtube.com/shorts/VIDEO_ID
        Returns an empty string if no usable URL is configured.
        """
        import re
        from urllib.parse import urlparse, parse_qs

        raw = (self.intro_video_embed_url or self.intro_video_url or '').strip()
        if not raw:
            return ''

        video_id = ''
        try:
            parsed = urlparse(raw)
            host = (parsed.netloc or '').lower()
            if host.startswith('www.'):
                host = host[4:]
            path = parsed.path or ''
            if host == 'youtu.be':
                video_id = path.lstrip('/').split('/')[0]
            elif host.endswith('youtube.com') or host.endswith('youtube-nocookie.com'):
                if path.startswith('/embed/'):
                    video_id = path[len('/embed/'):].split('/')[0]
                elif path.startswith('/shorts/'):
                    video_id = path[len('/shorts/'):].split('/')[0]
                elif path == '/watch':
                    video_id = (parse_qs(parsed.query or '').get('v') or [''])[0]
        except Exception:
            video_id = ''

        if not video_id:
            match = re.search(
                r'(?:v=|/embed/|/shorts/|youtu\.be/)([A-Za-z0-9_-]{6,})',
                raw,
            )
            if match:
                video_id = match.group(1)

        if not video_id:
            return ''

        return (
            f'https://www.youtube.com/embed/{video_id}'
            '?autoplay=1&rel=0&playsinline=1'
        )


# ── FooterSettings ────────────────────────────────────────────────────────────

class FooterSettings(_SingletonMixin):
    """Footer settings"""
    company_name = models.CharField(max_length=100, default='Adonis Group', verbose_name='Company Name')
    description = models.TextField(blank=True, verbose_name='Description')
    copyright_text = models.CharField(max_length=200, blank=True, verbose_name='Copyright Text')
    address = models.TextField(blank=True, verbose_name='Address')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Phone')
    phone_number_2 = models.CharField(max_length=20, blank=True, verbose_name='Second Phone')
    email = models.EmailField(blank=True, verbose_name='Email')
    instagram_url = models.URLField(max_length=200, blank=True, verbose_name='Instagram URL')
    facebook_url = models.URLField(max_length=200, blank=True, verbose_name='Facebook URL')
    linkedin_url = models.URLField(max_length=200, blank=True, verbose_name='LinkedIn URL')
    x_url = models.URLField(max_length=200, blank=True, verbose_name='X (Twitter) URL')
    youtube_url = models.URLField(max_length=200, blank=True, verbose_name='YouTube URL')
    whatsapp_number = models.CharField(max_length=100, blank=True, verbose_name='WhatsApp Number')
    whatsapp_button_text = models.CharField(max_length=50, default='Chat Now', verbose_name='WhatsApp Button Text')

    class Meta:
        verbose_name = 'Footer Settings'
        verbose_name_plural = 'Footer Settings'

    def __str__(self):
        return 'Footer Settings'


# ── Service ───────────────────────────────────────────────────────────────────

class Service(models.Model):
    title = models.CharField(max_length=100, verbose_name='Title')
    description = models.TextField(verbose_name='Description')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icon')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['order']

    def __str__(self):
        return self.title


# ── ProcessStep ───────────────────────────────────────────────────────────────

class ProcessStep(models.Model):
    step_number = models.PositiveIntegerField(verbose_name='Step Number')
    title = models.CharField(max_length=100, verbose_name='Title')
    description = models.TextField(verbose_name='Description')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icon')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Process Step'
        verbose_name_plural = 'Process Steps'
        ordering = ['step_number']

    def __str__(self):
        return f'{self.step_number}. {self.title}'


# ── ContactSubmission ─────────────────────────────────────────────────────────

REQUEST_TYPES = [('general', 'General'), ('property', 'Property'), ('golden_visa', 'Golden Visa'), ('customer', 'Customer'), ('agent', 'Agent'), ('partnership', 'Partnership'), ('other', 'Other')]


class ContactSubmission(SoftDeleteModel):
    full_name = models.CharField(max_length=100, verbose_name='Full Name')
    phone = models.CharField(max_length=30, verbose_name='Phone')
    email = models.EmailField(blank=True, verbose_name='Email')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='general', verbose_name='Request Type')
    message = models.TextField(blank=True, verbose_name='Message')
    property_interest = models.CharField(max_length=200, blank=True, verbose_name='Property Interest')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    is_read = models.BooleanField(default=False, verbose_name='Read')
    notes = models.TextField(blank=True, verbose_name='Internal Notes')
    source = models.CharField(max_length=60, blank=True, verbose_name='Source')

    class Meta:
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} — {self.created_at:%Y-%m-%d}'


# ── ChatLead ──────────────────────────────────────────────────────────────────

class ChatLead(SoftDeleteModel):
    LEAD_SCORE_CHOICES = [('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold'), ('unknown', 'Unknown')]
    STATUS_CHOICES = [('new', 'New'), ('contacted', 'Contacted'), ('qualified', 'Qualified'), ('closed', 'Closed'), ('lost', 'Lost')]
    SOURCE_CHOICES = [('chat', 'Chat'), ('landing', 'Landing'), ('other', 'Other')]

    name = models.CharField(max_length=100, verbose_name='Name')
    phone = models.CharField(max_length=30, verbose_name='Phone')
    topic = models.CharField(max_length=200, blank=True, verbose_name='Topic')
    page_url = models.CharField(max_length=500, blank=True, verbose_name='Page URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    is_read = models.BooleanField(default=False, verbose_name='Read')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Assigned To')
    conversation_json = models.TextField(blank=True, null=True, verbose_name='Conversation JSON')
    country = models.CharField(max_length=80, blank=True, null=True, verbose_name='Country')
    follow_up_date = models.DateField(null=True, blank=True, verbose_name='Follow-up Date')
    internal_notes = models.TextField(blank=True, verbose_name='Internal Notes')
    last_contact_at = models.DateTimeField(null=True, blank=True, verbose_name='Last Contact At')
    lead_score = models.CharField(max_length=10, choices=LEAD_SCORE_CHOICES, default='unknown', verbose_name='Lead Score')
    source_page = models.CharField(max_length=200, blank=True, verbose_name='Source Page')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Status')
    summary = models.TextField(blank=True, verbose_name='Summary')
    language = models.CharField(max_length=10, blank=True, verbose_name='Language')
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='chat', verbose_name='Source')
    telegram_sent = models.BooleanField(default=False, verbose_name='Telegram Sent')
    telegram_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Telegram Sent At')

    class Meta:
        verbose_name = 'Chat Lead'
        verbose_name_plural = 'Chat Leads'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.phone})'


# ── PartnerLead ───────────────────────────────────────────────────────────────

class PartnerLead(models.Model):
    PARTNER_TYPE_CHOICES = [
        ('broker', 'Broker'),
        ('agent', 'Agent'),
        ('lawyer', 'Lawyer'),
        ('client', 'Client'),
        ('accountant', 'Accountant'),
        ('other', 'Other'),
    ]

    first_name = models.CharField(max_length=80, verbose_name='First Name')
    last_name = models.CharField(max_length=80, verbose_name='Last Name')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=30, verbose_name='Phone')
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPE_CHOICES, verbose_name='Partner Type')
    other_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='Other Title')
    country = models.CharField(max_length=80, blank=True, null=True, verbose_name='Country')
    company = models.CharField(max_length=120, blank=True, null=True, verbose_name='Company')
    message = models.TextField(blank=True, null=True, verbose_name='Message')
    consent = models.BooleanField(default=False, verbose_name='Consent')
    source = models.CharField(max_length=40, blank=True, verbose_name='Source')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Partner Lead'
        verbose_name_plural = 'Partner Leads'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


# ── Customer ──────────────────────────────────────────────────────────────────

class Customer(SoftDeleteModel):
    full_name = models.CharField(max_length=120, verbose_name='Full Name')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Phone')
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


# ── ChatMessage ───────────────────────────────────────────────────────────────

class ChatMessage(SoftDeleteModel):
    DIRECTION_CHOICES = [('inbound', 'Inbound'), ('outbound', 'Outbound'), ('system', 'System')]

    lead = models.ForeignKey(ChatLead, null=True, blank=True, on_delete=models.SET_NULL, related_name='messages', verbose_name='Lead')
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Customer')
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, default='inbound', verbose_name='Direction')
    message = models.TextField(verbose_name='Message')
    metadata = models.TextField(blank=True, null=True, verbose_name='Metadata (JSON)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.direction}: {self.message[:50]}'


# ── ChatSession ───────────────────────────────────────────────────────────────

class ChatSession(models.Model):
    PHASE_CHOICES = [('greeting', 'Greeting'), ('qualification', 'Qualification'), ('handover', 'Handover'), ('closed', 'Closed')]

    session_key = models.CharField(max_length=64, unique=True, verbose_name='Session Key')
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='greeting', verbose_name='Phase')
    lead = models.ForeignKey(ChatLead, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Lead')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Agent')
    agent_notified_at = models.DateTimeField(null=True, blank=True, verbose_name='Agent Notified At')
    page_url = models.CharField(max_length=500, blank=True, verbose_name='Page URL')
    visitor_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Visitor IP')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f'Session {self.session_key[:8]}'


# ── ChatSessionMessage ────────────────────────────────────────────────────────

class ChatSessionMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='Session')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='Role')
    content = models.TextField(verbose_name='Content')
    is_read = models.BooleanField(default=False, verbose_name='Read')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Session Message'
        verbose_name_plural = 'Session Messages'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:50]}'


# ── Testimonial ───────────────────────────────────────────────────────────────

class Testimonial(SEOContentInterface, models.Model):
    client_name = models.CharField(max_length=100, verbose_name='Client Name')
    client_country = models.CharField(max_length=50, blank=True, verbose_name='Client Country')
    content = models.TextField(verbose_name='Testimonial Content')
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='Rating')
    image = models.ImageField(upload_to='testimonials/', blank=True, verbose_name='Client Photo')
    image_alt = models.CharField(max_length=200, blank=True, verbose_name='Image ALT Text')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    seo_title = models.CharField(max_length=70, blank=True, verbose_name='SEO Title')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Meta Description')
    robots_index = models.BooleanField(default=True, verbose_name='Robots Index')
    robots_follow = models.BooleanField(default=True, verbose_name='Robots Follow')
    seo_allow_publish_override = models.BooleanField(default=False, verbose_name='Allow Publish Override')

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.client_name} — {self.client_country}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('testimonial_detail', kwargs={'pk': self.pk})


# ── FAQ ───────────────────────────────────────────────────────────────────────

class FAQ(models.Model):
    question = models.CharField(max_length=300, verbose_name='Question')
    answer = models.TextField(verbose_name='Answer')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order']

    def __str__(self):
        return self.question[:80]


# ── AboutPageSettings ─────────────────────────────────────────────────────────

class AboutPageSettings(_SingletonMixin):
    """About Us page settings – editable from admin"""
    hero_title = models.CharField(max_length=200, default='Your Trusted Partner for Greek Residency', verbose_name='Hero Title')
    hero_subtitle = models.TextField(default='Built on experience, driven by trust, focused on your future in Europe', verbose_name='Hero Subtitle')
    # Hero visual — new fields
    hero_image = models.ImageField(
        upload_to='about/',
        blank=True,
        null=True,
        verbose_name='تصویر Hero (About Us)',
        help_text='تصویر پس‌زمینه بخش Hero. اگر آپلود نشود، گرادیان آبی نمایش داده می‌شود. اندازه پیشنهادی: ۱۹۲۰×۷۰۰ پیکسل.',
    )
    hero_video_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='لینک ویدئو Hero (About Us)',
        help_text='لینک یوتیوب یا URL ویدئو برای پس‌زمینه Hero. اگر هم تصویر و هم لینک وارد شده باشد، تصویر اولویت دارد.',
    )
    # Office media
    office_video = models.FileField(upload_to='about/', blank=True, null=True, verbose_name='Office Video')
    office_video_poster = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name='Video Poster Image')
    office_image_1 = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name='Office Image 1')
    office_image_2 = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name='Office Image 2')
    office_image_3 = models.ImageField(upload_to='about/', blank=True, null=True, verbose_name='Office Image 3')
    about_exterior_image = models.ImageField(
        upload_to='about/',
        blank=True,
        null=True,
        verbose_name='Company Exterior Image',
        help_text='Photo of the company building exterior, shown next to the "Who We Are" text.',
    )
    # Text
    about_title = models.CharField(max_length=200, default='Who We Are', verbose_name='About Section Title')
    about_text = RichTextField(blank=True, verbose_name='About Text')
    # Team
    team_title = models.CharField(max_length=100, default='Our Team', verbose_name='Team Section Title')
    team_subtitle = models.TextField(blank=True, verbose_name='Team Section Subtitle')

    class Meta:
        verbose_name = 'About Page Settings'
        verbose_name_plural = 'About Page Settings'

    def __str__(self):
        return 'About Page Settings'


# ── Office ────────────────────────────────────────────────────────────────────

class Office(models.Model):
    city = models.CharField(max_length=100, verbose_name='City')
    country = models.CharField(max_length=100, verbose_name='Country')
    address = models.TextField(verbose_name='Address')
    phone_number = models.CharField(max_length=50, blank=True, verbose_name='Phone')
    email = models.EmailField(blank=True, verbose_name='Email')
    map_embed_url = models.TextField(blank=True, verbose_name='Map Embed URL')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Office'
        verbose_name_plural = 'Offices'
        ordering = ['order']

    def __str__(self):
        return f'{self.city}, {self.country}'


# ── TeamMember ────────────────────────────────────────────────────────────────

class TeamMember(models.Model):
    name = models.CharField(max_length=100, verbose_name='Name')
    position = models.CharField(max_length=100, verbose_name='Position')
    photo = models.ImageField(upload_to='team/', blank=True, null=True, verbose_name='Photo')
    bio = models.TextField(blank=True, verbose_name='Bio')
    linkedin_url = models.URLField(max_length=200, blank=True, verbose_name='LinkedIn URL')
    email = models.EmailField(blank=True, verbose_name='Email')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
        ordering = ['order']

    def __str__(self):
        return self.name


# ── FrontPageSettings ─────────────────────────────────────────────────────────

class FrontPageSettings(_SingletonMixin):
    heading_font = models.CharField(max_length=50, blank=True, verbose_name='Heading Font')
    body_font = models.CharField(max_length=50, blank=True, verbose_name='Body Font')
    heading_size = models.PositiveIntegerField(default=36, verbose_name='Heading Size')
    body_size = models.PositiveIntegerField(default=16, verbose_name='Body Size')
    services_badge = models.CharField(max_length=100, blank=True, verbose_name='Services Badge')
    services_title = models.CharField(max_length=200, blank=True, verbose_name='Services Title')
    services_description = models.TextField(blank=True, verbose_name='Services Description')
    process_badge = models.CharField(max_length=100, blank=True, verbose_name='Process Badge')
    process_title = models.CharField(max_length=200, blank=True, verbose_name='Process Title')
    process_description = models.TextField(blank=True, verbose_name='Process Description')
    catalogue_badge_text = models.CharField(max_length=100, blank=True, verbose_name='Catalogue Badge')
    catalogue_heading = models.CharField(max_length=200, blank=True, verbose_name='Catalogue Heading')
    catalogue_subtext = models.TextField(blank=True, verbose_name='Catalogue Subtext')
    catalogue_btn1_title = models.CharField(max_length=200, blank=True, verbose_name='Catalogue Button 1 Title')
    catalogue_btn1_label = models.CharField(max_length=100, blank=True, verbose_name='Catalogue Button 1 Label')
    catalogue_btn1_pdf = models.FileField(upload_to='catalogue/', blank=True, null=True, verbose_name='Catalogue PDF 1')
    catalogue_btn2_title = models.CharField(max_length=200, blank=True, verbose_name='Catalogue Button 2 Title')
    catalogue_btn2_label = models.CharField(max_length=100, blank=True, verbose_name='Catalogue Button 2 Label')
    catalogue_btn2_pdf = models.FileField(upload_to='catalogue/', blank=True, null=True, verbose_name='Catalogue PDF 2')
    contact_badge = models.CharField(max_length=100, blank=True, verbose_name='Contact Badge')
    contact_title = models.CharField(max_length=200, blank=True, verbose_name='Contact Title')
    contact_description = models.TextField(blank=True, verbose_name='Contact Description')
    body_color = models.CharField(max_length=20, blank=True, verbose_name='Body Color')

    class Meta:
        verbose_name = 'Front Page Settings'
        verbose_name_plural = 'Front Page Settings'

    def __str__(self):
        return 'Front Page Settings'


# ── BlogCategory ──────────────────────────────────────────────────────────────

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Category Name')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL Slug')
    description = models.TextField(blank=True, verbose_name='Description')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


# ── BlogPost ──────────────────────────────────────────────────────────────────

class BlogPost(SEOContentInterface, models.Model):
    title = models.CharField(max_length=200, verbose_name='Title')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='URL Slug')
    category = models.ForeignKey(BlogCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='posts', verbose_name='Category')
    excerpt = models.TextField(blank=True, verbose_name='Excerpt / Summary', help_text='Short summary shown in blog list. Supports bold, italic, links.')
    content = CKEditor5Field(config_name='blog', verbose_name='Content')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True, verbose_name='Featured Image')
    featured_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Featured Image ALT')
    meta_title = models.CharField(max_length=70, blank=True, verbose_name='SEO Title')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Meta Description')
    focus_keyword = models.CharField(max_length=120, blank=True, verbose_name='Focus Keyword')
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name='Meta Keywords')
    canonical_url = models.CharField(max_length=200, blank=True, verbose_name='Canonical URL')
    robots_index = models.BooleanField(default=True, verbose_name='Robots Index')
    noindex = models.BooleanField(default=False, verbose_name='Noindex')
    robots_follow = models.BooleanField(default=True, verbose_name='Robots Follow')
    seo_status = models.CharField(
        max_length=20,
        choices=SEO_STATUS_CHOICES,
        default='needs_review',
        verbose_name='SEO Status',
    )
    seo_allow_publish_override = models.BooleanField(default=False, verbose_name='Allow Publish Override')
    og_title = models.CharField(max_length=100, blank=True, verbose_name='OG Title')
    og_description = models.CharField(max_length=200, blank=True, verbose_name='OG Description')
    og_image = models.ImageField(upload_to='blog/og/', blank=True, null=True, verbose_name='OG Image')
    author = models.CharField(max_length=100, blank=True, verbose_name='Author')
    published_date = models.DateField(default=timezone.now, verbose_name='Published Date')
    is_published = models.BooleanField(default=False, verbose_name='Published')
    is_featured = models.BooleanField(default=False, verbose_name='Featured')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    views = models.PositiveIntegerField(default=0, verbose_name='Views')

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def get_h1(self, lang=None):
        return self.title or ''

    def get_seo_title(self, lang=None):
        return self.meta_title or self.title or ''

    def get_meta_description(self, lang=None):
        from django.utils.html import strip_tags
        return self.meta_description or strip_tags(self.excerpt or '')[:160]


# ── PartnershipPageSettings ───────────────────────────────────────────────────

class PartnershipPageSettings(_SingletonMixin):
    hero_title = models.CharField(max_length=200, blank=True, verbose_name='Hero Title')
    hero_subtitle = models.TextField(blank=True, verbose_name='Hero Subtitle')
    hero_image = models.ImageField(upload_to='partnerships/', blank=True, null=True, verbose_name='Hero Image')
    video = models.FileField(upload_to='partnerships/', blank=True, null=True, verbose_name='Video')
    video_cover = models.ImageField(upload_to='partnerships/', blank=True, null=True, verbose_name='Video Cover')
    video_title = models.CharField(max_length=200, blank=True, verbose_name='Video Title')
    video_subtitle = models.TextField(blank=True, verbose_name='Video Subtitle')
    video_url = models.CharField(max_length=500, blank=True, verbose_name='Video URL')
    b2b_title = models.CharField(max_length=200, blank=True, verbose_name='B2B Title')
    b2b_text = models.TextField(blank=True, verbose_name='B2B Text')
    b2b_image = models.ImageField(upload_to='partnerships/', blank=True, null=True, verbose_name='B2B Image')
    benefit_1_icon = models.CharField(max_length=50, blank=True, verbose_name='Benefit 1 Icon')
    benefit_1_title = models.CharField(max_length=100, blank=True, verbose_name='Benefit 1 Title')
    benefit_1_text = models.TextField(blank=True, verbose_name='Benefit 1 Text')
    benefit_2_icon = models.CharField(max_length=50, blank=True, verbose_name='Benefit 2 Icon')
    benefit_2_title = models.CharField(max_length=100, blank=True, verbose_name='Benefit 2 Title')
    benefit_2_text = models.TextField(blank=True, verbose_name='Benefit 2 Text')
    benefit_3_icon = models.CharField(max_length=50, blank=True, verbose_name='Benefit 3 Icon')
    benefit_3_title = models.CharField(max_length=100, blank=True, verbose_name='Benefit 3 Title')
    benefit_3_text = models.TextField(blank=True, verbose_name='Benefit 3 Text')
    benefit_4_icon = models.CharField(max_length=50, blank=True, verbose_name='Benefit 4 Icon')
    benefit_4_title = models.CharField(max_length=100, blank=True, verbose_name='Benefit 4 Title')
    benefit_4_text = models.TextField(blank=True, verbose_name='Benefit 4 Text')
    benefit_5_icon = models.CharField(max_length=50, blank=True, verbose_name='Benefit 5 Icon')
    benefit_5_title = models.CharField(max_length=100, blank=True, verbose_name='Benefit 5 Title')
    benefit_5_text = models.TextField(blank=True, verbose_name='Benefit 5 Text')
    benefit_6_icon = models.CharField(max_length=50, blank=True, verbose_name='Benefit 6 Icon')
    benefit_6_title = models.CharField(max_length=100, blank=True, verbose_name='Benefit 6 Title')
    benefit_6_text = models.TextField(blank=True, verbose_name='Benefit 6 Text')
    cta_title = models.CharField(max_length=200, blank=True, verbose_name='CTA Title')
    cta_text = models.TextField(blank=True, verbose_name='CTA Text')
    cta_button_text = models.CharField(max_length=50, blank=True, verbose_name='CTA Button Text')

    class Meta:
        verbose_name = 'Partnership Page Settings'
        verbose_name_plural = 'Partnership Page Settings'

    def __str__(self):
        return 'Partnership Page Settings'


# ── PropertiesPageSettings ────────────────────────────────────────────────────

class PropertiesPageSettings(_SingletonMixin):
    hero_title = models.CharField(max_length=200, blank=True, verbose_name='Hero Title')
    hero_subtitle = models.TextField(blank=True, verbose_name='Hero Subtitle')
    hero_badge = models.CharField(max_length=100, blank=True, verbose_name='Hero Badge')
    hero_video = models.FileField(upload_to='properties/', blank=True, null=True, verbose_name='Hero Video')
    hero_video_poster = models.ImageField(upload_to='properties/', blank=True, null=True, verbose_name='Video Poster')
    hero_image = models.ImageField(upload_to='properties/', blank=True, null=True, verbose_name='Hero Image')
    intro_title = models.CharField(max_length=200, blank=True, verbose_name='Intro Title')
    intro_text = models.TextField(blank=True, verbose_name='Intro Text')

    class Meta:
        verbose_name = 'Properties Page Settings'
        verbose_name_plural = 'Properties Page Settings'

    def __str__(self):
        return 'Properties Page Settings'


# ── GoldenVisaCard ────────────────────────────────────────────────────────────

class GoldenVisaCard(SEOContentInterface, models.Model):
    title = models.CharField(max_length=200, verbose_name='Title')
    subtitle = models.CharField(max_length=300, blank=True, verbose_name='Subtitle')
    description = models.TextField(blank=True, verbose_name='Description')
    price_amount = models.CharField(max_length=50, blank=True, verbose_name='Price Amount')
    price_label = models.CharField(max_length=100, blank=True, verbose_name='Price Label')
    image = models.ImageField(upload_to='golden_visa/', blank=True, null=True, verbose_name='Image')
    image_alt = models.CharField(max_length=200, blank=True, verbose_name='Image ALT')
    detail_page_url = models.CharField(max_length=200, blank=True, verbose_name='Detail Page URL')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Golden Visa Card'
        verbose_name_plural = 'Golden Visa Cards'
        ordering = ['order']

    def __str__(self):
        return self.title


# ── AuditLog ──────────────────────────────────────────────────────────────────

class AuditLog(models.Model):
    ACTION_CHOICES = [('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'), ('archive', 'Archive'), ('restore', 'Restore'), ('view', 'View')]

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Actor')
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Content Type')
    object_id = models.CharField(max_length=64, verbose_name='Object ID')
    object_ref = models.CharField(max_length=255, blank=True, verbose_name='Object Reference')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name='Action')
    changes = models.TextField(blank=True, null=True, verbose_name='Changes (JSON)')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} — {self.object_ref} — {self.created_at:%Y-%m-%d %H:%M}'


# ── ErrorLog ──────────────────────────────────────────────────────────────────

class ErrorLog(models.Model):
    error_type = models.CharField(max_length=200, verbose_name='Error Type')
    error_message = models.TextField(verbose_name='Error Message')
    traceback = models.TextField(blank=True, verbose_name='Traceback')
    url = models.CharField(max_length=500, blank=True, verbose_name='URL')
    method = models.CharField(max_length=10, blank=True, verbose_name='HTTP Method')
    user_agent = models.CharField(max_length=500, blank=True, verbose_name='User Agent')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP Address')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='User')
    request_data = models.TextField(blank=True, null=True, verbose_name='Request Data (JSON)')
    is_read = models.BooleanField(default=False, verbose_name='Read')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Error Log'
        verbose_name_plural = 'Error Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.error_type} — {self.created_at:%Y-%m-%d %H:%M}'


# ── Event ─────────────────────────────────────────────────────────────────────

class Event(SEOContentInterface, models.Model):
    title = models.CharField(max_length=200, verbose_name='Title')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL Slug')
    short_description = models.CharField(max_length=300, blank=True, verbose_name='Short Description')
    full_description = CKEditor5Field(config_name='event', blank=True, verbose_name='Full Description')
    thumbnail = models.ImageField(upload_to='events/', verbose_name='Thumbnail')
    thumbnail_alt = models.CharField(max_length=200, blank=True, verbose_name='Thumbnail ALT')
    video_file = models.FileField(upload_to='events/', blank=True, null=True, verbose_name='Video File')
    video_url = models.CharField(max_length=200, blank=True, verbose_name='Video URL')
    event_date = models.DateField(null=True, blank=True, verbose_name='Event Date')
    location = models.CharField(max_length=200, blank=True, verbose_name='Location')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    seo_title = models.CharField(max_length=70, blank=True, verbose_name='SEO Title')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Meta Description')
    focus_keyword = models.CharField(max_length=120, blank=True, verbose_name='Focus Keyword')
    canonical_url = models.CharField(max_length=200, blank=True, verbose_name='Canonical URL')
    og_image = models.ImageField(upload_to='events/og/', blank=True, null=True, verbose_name='OG Image')
    robots_index = models.BooleanField(default=True, verbose_name='Robots Index')
    robots_follow = models.BooleanField(default=True, verbose_name='Robots Follow')
    seo_allow_publish_override = models.BooleanField(default=False, verbose_name='Allow Publish Override')

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['order', '-event_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('event_detail', kwargs={'slug': self.slug})


# ── EventImage ────────────────────────────────────────────────────────────────

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images', verbose_name='Event')
    image = models.ImageField(upload_to='events/gallery/', verbose_name='Image')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Caption')
    order = models.PositiveIntegerField(default=0, verbose_name='Order')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Event Image'
        verbose_name_plural = 'Event Images'
        ordering = ['order']

    def __str__(self):
        return f'Image for {self.event}'


# ── GoldenVisaLandingPage ─────────────────────────────────────────────────────

class GoldenVisaLandingPage(models.Model):
    """Singleton model for the /greece-golden-visa/ landing page content."""
    hero_title = models.CharField(max_length=200, default='Greek Golden Visa', verbose_name='Hero Title')
    hero_subtitle = models.TextField(blank=True, verbose_name='Hero Subtitle')
    hero_image = models.ImageField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Hero Background Image')
    hero_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Hero Image ALT Text')
    hero_video = models.FileField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Hero Video')
    hero_video_opacity = models.PositiveIntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Hero Video Opacity (%)')
    intro_text = CKEditor5Field(config_name='blog', blank=True, verbose_name='Intro Text')
    section_1_title = models.CharField(max_length=200, blank=True, verbose_name='Section 1 Title')
    section_1_text = CKEditor5Field(config_name='blog', blank=True, verbose_name='Section 1 Text')
    section_1_image = models.ImageField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Section 1 Image')
    section_1_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Section 1 Image ALT')
    section_2_title = models.CharField(max_length=200, blank=True, verbose_name='Section 2 Title')
    section_2_text = CKEditor5Field(config_name='blog', blank=True, verbose_name='Section 2 Text')
    section_2_image = models.ImageField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Section 2 Image')
    section_2_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Section 2 Image ALT')
    section_3_title = models.CharField(max_length=200, blank=True, verbose_name='Section 3 Title')
    section_3_text = CKEditor5Field(config_name='blog', blank=True, verbose_name='Section 3 Text')
    section_3_image = models.ImageField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Section 3 Image')
    section_3_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Section 3 Image ALT')
    tier_250_title = models.CharField(max_length=200, blank=True, verbose_name='Tier €250K Title')
    tier_250_desc = models.TextField(blank=True, verbose_name='Tier €250K Description')
    tier_250_image = models.ImageField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Tier €250K Image')
    tier_250_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Tier €250K Image ALT')
    tier_400_title = models.CharField(max_length=200, blank=True, verbose_name='Tier €400K Title')
    tier_400_desc = models.TextField(blank=True, verbose_name='Tier €400K Description')
    tier_400_image = models.ImageField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Tier €400K Image')
    tier_400_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Tier €400K Image ALT')
    tier_800_title = models.CharField(max_length=200, blank=True, verbose_name='Tier €800K Title')
    tier_800_desc = models.TextField(blank=True, verbose_name='Tier €800K Description')
    tier_800_image = models.ImageField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Tier €800K Image')
    tier_800_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Tier €800K Image ALT')
    benefits_title = models.CharField(max_length=200, blank=True, verbose_name='Benefits Title')
    benefits_text = models.TextField(blank=True, verbose_name='Benefits Text')
    benefits_bg_image = models.ImageField(upload_to='golden_visa_landing/', blank=True, null=True, verbose_name='Benefits Background Image')
    process_title = models.CharField(max_length=200, blank=True, verbose_name='Process Title')
    process_steps = models.TextField(blank=True, verbose_name='Process Steps (JSON)')
    short_video_urls = models.TextField(blank=True, verbose_name='Short Video URLs (JSON)')
    short_video_url_1 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 1')
    short_video_url_2 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 2')
    short_video_url_3 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 3')
    short_video_url_4 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 4')
    short_video_url_5 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 5')
    meta_title = models.CharField(max_length=100, blank=True, verbose_name='Meta Title')
    meta_description = models.CharField(max_length=180, blank=True, verbose_name='Meta Description')
    canonical_url = models.CharField(max_length=300, blank=True, verbose_name='Canonical URL')
    og_title = models.CharField(max_length=120, blank=True, verbose_name='OG Title')
    og_description = models.CharField(max_length=220, blank=True, verbose_name='OG Description')
    og_image = models.ImageField(upload_to='golden_visa_landing/og/', blank=True, null=True, verbose_name='OG Image')
    focus_keyword = models.CharField(max_length=160, blank=True, verbose_name='Focus Keyword')
    noindex = models.BooleanField(default=False, verbose_name='Noindex')
    seo_status = models.CharField(
        max_length=20,
        choices=SEO_STATUS_CHOICES,
        default='needs_review',
        verbose_name='SEO Status',
    )
    robots_index = models.BooleanField(default=True, verbose_name='Robots Index')
    robots_follow = models.BooleanField(default=True, verbose_name='Robots Follow')
    is_published = models.BooleanField(default=True, verbose_name='Published')

    class Meta:
        verbose_name = 'Golden Visa Landing Page (EN/TR)'
        verbose_name_plural = 'Golden Visa Landing Page (EN/TR)'

    def __str__(self):
        return 'Golden Visa Landing Page (EN/TR)'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ── GoldenVisaFaLandingPage ───────────────────────────────────────────────────

class GoldenVisaFaLandingPage(models.Model):
    """Singleton model for the Persian ads landing page: /fa/greece-golden-visa/."""

    hero_title = models.CharField(max_length=220, default='Greek Golden Visa', verbose_name='Hero Title (FA Landing)')
    hero_subtitle = models.TextField(blank=True, verbose_name='Hero Subtitle (FA Landing)')
    hero_cta_text = models.CharField(max_length=120, default='Get Free Consultation', verbose_name='Hero CTA Button Text')
    hero_image = models.ImageField(upload_to='golden_visa_fa_landing/', blank=True, null=True, verbose_name='Hero Background Image')
    hero_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Hero Image ALT Text')
    hero_video = models.FileField(upload_to='golden_visa_fa_landing/', blank=True, null=True, verbose_name='Hero Video')
    hero_image_opacity = models.PositiveIntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Hero Image Darkness (%)', help_text='0 = brightest image, 100 = darkest image.')
    hero_content_vertical_align = models.CharField(max_length=12, default='bottom', choices=[('top', 'Top'), ('center', 'Center'), ('bottom', 'Bottom')], verbose_name='Hero Content Vertical Position')
    hero_content_horizontal_align = models.CharField(max_length=12, default='right', choices=[('right', 'Right'), ('center', 'Center'), ('left', 'Left')], verbose_name='Hero Content Horizontal Position')
    hero_title_color = models.CharField(max_length=20, default='#ffffff', verbose_name='رنگ فونت تیتر هیرو')
    hero_title_font_size = models.CharField(max_length=10, default='48px', verbose_name='سایز فونت تیتر هیرو')
    hero_subtitle_color = models.CharField(max_length=20, default='#ffffff', verbose_name='رنگ فونت ساب‌تایتل هیرو')
    hero_subtitle_font_size = models.CharField(max_length=10, default='20px', verbose_name='سایز فونت ساب‌تایتل هیرو')
    intro_title = models.CharField(max_length=220, blank=True, verbose_name='Intro Title')
    intro_text = CKEditor5Field(config_name='blog', blank=True, verbose_name='Intro Text')
    intro_image = models.ImageField(upload_to='golden_visa_fa_landing/', blank=True, null=True, verbose_name='Intro Image')
    intro_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Intro Image ALT')
    intro_bullet_1 = models.CharField(max_length=200, blank=True, default='اقامت دائم بدون شرط حضور', verbose_name='بولت اول')
    intro_bullet_2 = models.CharField(max_length=200, blank=True, default='شامل کل خانواده (همسر و فرزندان)', verbose_name='بولت دوم')
    intro_bullet_3 = models.CharField(max_length=200, blank=True, default='امکان سرمایه\u200cگذاری و درآمد اجاره\u200cای', verbose_name='بولت سوم')
    intro_feature_1_icon = models.CharField(max_length=10, blank=True, default='🏡', verbose_name='آیکون ویژگی اول')
    intro_feature_1_text = models.CharField(max_length=120, blank=True, default='ملک در قلب اروپا', verbose_name='متن ویژگی اول')
    intro_feature_2_icon = models.CharField(max_length=10, blank=True, default='🌍', verbose_name='آیکون ویژگی دوم')
    intro_feature_2_text = models.CharField(max_length=120, blank=True, default='سفر بدون ویزا به ۲۶ کشور شنگن', verbose_name='متن ویژگی دوم')
    intro_feature_3_icon = models.CharField(max_length=10, blank=True, default='⚖️', verbose_name='آیکون ویژگی سوم')
    intro_feature_3_text = models.CharField(max_length=120, blank=True, default='پشتیبانی حقوقی کامل', verbose_name='متن ویژگی سوم')
    tiers_title = models.CharField(max_length=220, blank=True, verbose_name='Tiers Section Title')
    tier_1_title = models.CharField(max_length=220, blank=True, verbose_name='Tier Card 1 — Title (FA)')
    tier_1_short_desc = models.CharField(max_length=320, blank=True, verbose_name='Tier Card 1 — Short Description (FA)')
    tier_1_long_desc = models.TextField(blank=True, verbose_name='Tier Card 1 — Long Description (FA)')
    tier_1_price_label = models.CharField(max_length=80, blank=True, verbose_name='Tier Card 1 — Price Label (FA)')
    tier_1_price_amount = models.CharField(max_length=80, blank=True, verbose_name='Tier Card 1 — Price Amount')
    tier_1_image = models.ImageField(upload_to='golden_visa_fa_landing/tiers/', blank=True, null=True, verbose_name='تصویر کارت اول')
    tier_1_image_alt = models.CharField(max_length=200, blank=True, verbose_name='متن جایگزین تصویر کارت اول (ALT)')
    tier_1_cta_text = models.CharField(max_length=80, blank=True, verbose_name='متن دکمه کارت اول')
    tier_2_title = models.CharField(max_length=220, blank=True, verbose_name='Tier Card 2 — Title (FA)')
    tier_2_short_desc = models.CharField(max_length=320, blank=True, verbose_name='Tier Card 2 — Short Description (FA)')
    tier_2_long_desc = models.TextField(blank=True, verbose_name='Tier Card 2 — Long Description (FA)')
    tier_2_price_label = models.CharField(max_length=80, blank=True, verbose_name='Tier Card 2 — Price Label (FA)')
    tier_2_price_amount = models.CharField(max_length=80, blank=True, verbose_name='Tier Card 2 — Price Amount')
    tier_2_image = models.ImageField(upload_to='golden_visa_fa_landing/tiers/', blank=True, null=True, verbose_name='تصویر کارت دوم')
    tier_2_image_alt = models.CharField(max_length=200, blank=True, verbose_name='متن جایگزین تصویر کارت دوم (ALT)')
    tier_2_cta_text = models.CharField(max_length=80, blank=True, verbose_name='متن دکمه کارت دوم')
    tier_3_title = models.CharField(max_length=220, blank=True, verbose_name='Tier Card 3 — Title (FA)')
    tier_3_short_desc = models.CharField(max_length=320, blank=True, verbose_name='Tier Card 3 — Short Description (FA)')
    tier_3_long_desc = models.TextField(blank=True, verbose_name='Tier Card 3 — Long Description (FA)')
    tier_3_price_label = models.CharField(max_length=80, blank=True, verbose_name='Tier Card 3 — Price Label (FA)')
    tier_3_price_amount = models.CharField(max_length=80, blank=True, verbose_name='Tier Card 3 — Price Amount')
    tier_3_image = models.ImageField(upload_to='golden_visa_fa_landing/tiers/', blank=True, null=True, verbose_name='تصویر کارت سوم')
    tier_3_image_alt = models.CharField(max_length=200, blank=True, verbose_name='متن جایگزین تصویر کارت سوم (ALT)')
    tier_3_cta_text = models.CharField(max_length=80, blank=True, verbose_name='متن دکمه کارت سوم')
    projects_title = models.CharField(max_length=220, blank=True, verbose_name='Projects Section Title')
    benefits_title = models.CharField(max_length=220, blank=True, verbose_name='Benefits Title')
    benefits_bg_image = models.ImageField(upload_to='golden_visa_fa_landing/', blank=True, null=True, verbose_name='Benefits Background Image')
    benefits_text = models.TextField(blank=True, verbose_name='Benefits Text')
    process_title = models.CharField(max_length=220, blank=True, verbose_name='Process Title')
    process_steps = models.TextField(blank=True, verbose_name='Process Steps (JSON)')
    # ── ۶ مرحله ثابت ─────────────────────────────────────────────────────────
    step_1_title    = models.CharField(max_length=220, blank=True, verbose_name='مرحله ۱ – عنوان')
    step_1_subtitle = models.TextField(blank=True, verbose_name='مرحله ۱ – توضیح')
    step_2_title    = models.CharField(max_length=220, blank=True, verbose_name='مرحله ۲ – عنوان')
    step_2_subtitle = models.TextField(blank=True, verbose_name='مرحله ۲ – توضیح')
    step_3_title    = models.CharField(max_length=220, blank=True, verbose_name='مرحله ۳ – عنوان')
    step_3_subtitle = models.TextField(blank=True, verbose_name='مرحله ۳ – توضیح')
    step_4_title    = models.CharField(max_length=220, blank=True, verbose_name='مرحله ۴ – عنوان')
    step_4_subtitle = models.TextField(blank=True, verbose_name='مرحله ۴ – توضیح')
    step_5_title    = models.CharField(max_length=220, blank=True, verbose_name='مرحله ۵ – عنوان')
    step_5_subtitle = models.TextField(blank=True, verbose_name='مرحله ۵ – توضیح')
    step_6_title    = models.CharField(max_length=220, blank=True, verbose_name='مرحله ۶ – عنوان')
    step_6_subtitle = models.TextField(blank=True, verbose_name='مرحله ۶ – توضیح')
    own_shorts_title = models.CharField(max_length=220, blank=True, verbose_name='Own Shorts Title')
    own_short_video_url_1 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 1')
    own_short_video_url_2 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 2')
    own_short_video_url_3 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 3')
    own_short_video_url_4 = models.CharField(max_length=500, blank=True, verbose_name='Short Video URL 4')
    own_shorts_more_url = models.CharField(max_length=500, blank=True, verbose_name='Own Shorts More URL')
    testimonial_shorts_title = models.CharField(max_length=220, blank=True, verbose_name='Testimonial Shorts Title')
    testimonial_short_video_url_1 = models.CharField(max_length=500, blank=True, verbose_name='Testimonial Video URL 1')
    testimonial_short_video_url_2 = models.CharField(max_length=500, blank=True, verbose_name='Testimonial Video URL 2')
    testimonial_short_video_url_3 = models.CharField(max_length=500, blank=True, verbose_name='Testimonial Video URL 3')
    testimonial_short_video_url_4 = models.CharField(max_length=500, blank=True, verbose_name='Testimonial Video URL 4')
    testimonial_shorts_more_url = models.CharField(max_length=500, blank=True, verbose_name='Testimonial Shorts More URL')
    seo_title = models.CharField(max_length=100, blank=True, verbose_name='SEO Title')
    meta_description = models.CharField(max_length=180, blank=True, verbose_name='Meta Description')
    canonical_url = models.CharField(max_length=300, blank=True, verbose_name='Canonical URL')
    og_title = models.CharField(max_length=120, blank=True, verbose_name='OG Title')
    og_description = models.CharField(max_length=220, blank=True, verbose_name='OG Description')
    og_image = models.ImageField(upload_to='golden_visa_fa_landing/og/', blank=True, null=True, verbose_name='OG Image')
    focus_keyword = models.CharField(max_length=160, blank=True, verbose_name='Focus Keyword')
    noindex = models.BooleanField(default=False, verbose_name='Noindex')
    seo_status = models.CharField(
        max_length=20,
        choices=SEO_STATUS_CHOICES,
        default='needs_review',
        verbose_name='SEO Status',
    )
    robots_index = models.BooleanField(default=True, verbose_name='Robots Index')
    robots_follow = models.BooleanField(default=True, verbose_name='Robots Follow')
    is_published = models.BooleanField(default=True, verbose_name='Published')
    fa_instagram_url = models.CharField(max_length=500, blank=True, verbose_name='Instagram URL (FA)')
    fa_linkedin_url = models.CharField(max_length=500, blank=True, verbose_name='LinkedIn URL (FA)')
    fa_telegram_url = models.CharField(max_length=500, blank=True, verbose_name='Telegram URL (FA)')
    fa_whatsapp_number = models.CharField(max_length=100, blank=True, verbose_name='شماره واتساپ اصلی')
    fa_whatsapp_number_2 = models.CharField(max_length=100, blank=True, verbose_name='شماره یا لینک واتساپ دوم')
    fa_x_url = models.CharField(max_length=500, blank=True, verbose_name='X (Twitter) URL (FA)')
    fa_youtube_url = models.CharField(max_length=500, blank=True, verbose_name='YouTube URL (FA)')
    # ── سکشن مزایای آدونیس (بعد از چرا گلدن ویزا) ──────────────────────────────
    adonis_feat_section_title    = models.CharField(max_length=220, blank=True, default='چرا آدونیس گروپ؟', verbose_name='سکشن مزایا – عنوان')
    adonis_feat_section_subtitle = models.CharField(max_length=400, blank=True, default='با بیش از یک دهه تجربه در بازار ملک یونان، آدونیس بهترین انتخاب برای سفر سرمایه‌گذاری شماست.', verbose_name='سکشن مزایا – زیرعنوان')
    adonis_feat_1_icon  = models.CharField(max_length=10, blank=True, default='🏆', verbose_name='مزیت ۱ – آیکون')
    adonis_feat_1_title = models.CharField(max_length=120, blank=True, default='تجربه ۱۰+ ساله', verbose_name='مزیت ۱ – عنوان')
    adonis_feat_1_text  = models.TextField(blank=True, default='بیش از یک دهه حضور فعال در بازار ملک یونان و راهنمایی صدها خانواده ایرانی.', verbose_name='مزیت ۱ – توضیح')
    adonis_feat_2_icon  = models.CharField(max_length=10, blank=True, default='🤝', verbose_name='مزیت ۲ – آیکون')
    adonis_feat_2_title = models.CharField(max_length=120, blank=True, default='خدمات کامل زیر یک سقف', verbose_name='مزیت ۲ – عنوان')
    adonis_feat_2_text  = models.TextField(blank=True, default='از انتخاب ملک تا دریافت کارت اقامت، تمامی مراحل را پیش روی شما مدیریت می‌کنیم.', verbose_name='مزیت ۲ – توضیح')
    adonis_feat_3_icon  = models.CharField(max_length=10, blank=True, default='🛡️', verbose_name='مزیت ۳ – آیکون')
    adonis_feat_3_title = models.CharField(max_length=120, blank=True, default='امنیت سرمایه‌گذاری', verbose_name='مزیت ۳ – عنوان')
    adonis_feat_3_text  = models.TextField(blank=True, default='تمام معاملات با پشتوانه حقوقی کامل و وکلای مجرب یونانی انجام می‌شود.', verbose_name='مزیت ۳ – توضیح')
    adonis_feat_4_icon  = models.CharField(max_length=10, blank=True, default='🌍', verbose_name='مزیت ۴ – آیکون')
    adonis_feat_4_title = models.CharField(max_length=120, blank=True, default='پشتیبانی فارسی‌زبان', verbose_name='مزیت ۴ – عنوان')
    adonis_feat_4_text  = models.TextField(blank=True, default='تیم ما به زبان فارسی در کنار شماست و هیچ سوالی بی‌پاسخ نمی‌ماند.', verbose_name='مزیت ۴ – توضیح')
    adonis_feat_5_icon  = models.CharField(max_length=10, blank=True, default='🏙️', verbose_name='مزیت ۵ – آیکون')
    adonis_feat_5_title = models.CharField(max_length=120, blank=True, verbose_name='مزیت ۵ – عنوان')
    adonis_feat_5_text  = models.TextField(blank=True, verbose_name='مزیت ۵ – توضیح')
    adonis_feat_6_icon  = models.CharField(max_length=10, blank=True, default='⭐', verbose_name='مزیت ۶ – آیکون')
    adonis_feat_6_title = models.CharField(max_length=120, blank=True, verbose_name='مزیت ۶ – عنوان')
    adonis_feat_6_text  = models.TextField(blank=True, verbose_name='مزیت ۶ – توضیح')

    why_adonis_title = models.CharField(max_length=200, blank=True, default='چرا آدونیس؟', verbose_name='عنوان سکشن چرا آدونیس')
    why_adonis_subtitle = models.CharField(max_length=300, blank=True, default='با بیش از یک دهه تجربه در بازار ملک یونان، آدونیس تنها انتخاب مطمئن شماست.', verbose_name='زیرعنوان سکشن چرا آدونیس')
    why_item_1_icon = models.CharField(max_length=10, blank=True, default='🏆', verbose_name='آیکون دلیل اول')
    why_item_1_title = models.CharField(max_length=120, blank=True, default='تجربه ۱۰+ ساله', verbose_name='عنوان دلیل اول')
    why_item_1_text = models.TextField(blank=True, verbose_name='توضیح دلیل اول')
    why_item_2_icon = models.CharField(max_length=10, blank=True, default='🤝', verbose_name='آیکون دلیل دوم')
    why_item_2_title = models.CharField(max_length=120, blank=True, default='خدمات کامل زیر یک سقف', verbose_name='عنوان دلیل دوم')
    why_item_2_text = models.TextField(blank=True, verbose_name='توضیح دلیل دوم')
    why_item_3_icon = models.CharField(max_length=10, blank=True, default='🛡️', verbose_name='آیکون دلیل سوم')
    why_item_3_title = models.CharField(max_length=120, blank=True, default='امنیت سرمایه\u200cگذاری', verbose_name='عنوان دلیل سوم')
    why_item_3_text = models.TextField(blank=True, verbose_name='توضیح دلیل سوم')
    why_item_4_icon = models.CharField(max_length=10, blank=True, default='🌍', verbose_name='آیکون دلیل چهارم')
    why_item_4_title = models.CharField(max_length=120, blank=True, default='پشتیبانی فارسی\u200cزبان', verbose_name='عنوان دلیل چهارم')
    why_item_4_text = models.TextField(blank=True, verbose_name='توضیح دلیل چهارم')
    why_adonis_bg_image = models.ImageField(upload_to='golden_visa_fa_landing/', blank=True, null=True, verbose_name='تصویر پس\u200cزمینه سکشن «چرا آدونیس؟»')
    why_adonis_overlay_opacity = models.IntegerField(default=55, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='تیرگی فیلتر روی تصویر (۰ تا ۱۰۰)', help_text='۰ = کاملاً شفاف، ۱۰۰ = کاملاً تیره. پیشنهاد: ۴۰ تا ۶۰')

    class Meta:
        verbose_name = 'Persian Golden Visa Landing Page (FA)'
        verbose_name_plural = 'Persian Golden Visa Landing Page (FA)'

    def __str__(self):
        return 'Persian Golden Visa Landing Page (FA)'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ── GoldenVisaFaProcessStep ───────────────────────────────────────────────────

class GoldenVisaFaProcessStep(models.Model):
    """Individual step in the Persian Golden Visa process timeline."""
    title = models.CharField(max_length=255, verbose_name='عنوان مرحله')
    description = models.TextField(blank=True, verbose_name='توضیح مرحله')
    step_number = models.PositiveSmallIntegerField(verbose_name='شماره مرحله')
    image = models.ImageField(
        upload_to='fa_process_steps/', blank=True, null=True,
        verbose_name='تصویر مرتبط',
    )
    icon = models.CharField(
        max_length=100, blank=True,
        verbose_name='آیکن (Font Awesome class)',
        help_text='مثلاً: fas fa-passport',
    )
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        ordering = ['display_order', 'step_number']
        verbose_name = 'مرحله گلدن ویزا (فارسی)'
        verbose_name_plural = 'مراحل گلدن ویزا (فارسی)'

    def __str__(self):
        return f'{self.step_number}. {self.title}'


# ── PageSEO ───────────────────────────────────────────────────────────────────

PAGE_CHOICES = [
    ('home', 'Home'), ('about', 'About'), ('properties', 'Properties'),
    ('partnerships', 'Partnerships'), ('contact', 'Contact'), ('golden_visa', 'Golden Visa'),
    ('blog', 'Blog'),
]


class PageSEO(models.Model):
    """Admin-editable SEO meta tags per page and per language."""
    page_key = models.CharField(max_length=50, unique=True, choices=PAGE_CHOICES, verbose_name='Page')
    meta_title_en = models.CharField(max_length=70, blank=True, verbose_name='Meta Title (EN)')
    meta_desc_en = models.CharField(max_length=160, blank=True, verbose_name='Meta Description (EN)')
    og_title_en = models.CharField(max_length=100, blank=True, verbose_name='OG Title (EN)')
    og_desc_en = models.CharField(max_length=200, blank=True, verbose_name='OG Description (EN)')
    meta_title_tr = models.CharField(max_length=70, blank=True, verbose_name='Meta Title (TR)')
    meta_desc_tr = models.CharField(max_length=160, blank=True, verbose_name='Meta Description (TR)')
    og_title_tr = models.CharField(max_length=100, blank=True, verbose_name='OG Title (TR)')
    og_desc_tr = models.CharField(max_length=200, blank=True, verbose_name='OG Description (TR)')
    canonical_url = models.CharField(max_length=300, blank=True, verbose_name='Canonical URL')
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True, verbose_name='OG Image')
    focus_keyword = models.CharField(max_length=160, blank=True, verbose_name='Focus Keyword')
    noindex = models.BooleanField(default=False, verbose_name='Noindex')
    seo_status = models.CharField(
        max_length=20,
        choices=SEO_STATUS_CHOICES,
        default='needs_review',
        verbose_name='SEO Status',
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Page SEO'
        verbose_name_plural = 'Page SEO Settings'

    def __str__(self):
        return f'SEO: {self.page_key}'

    @classmethod
    def for_page(cls, key):
        obj, _ = cls.objects.get_or_create(page_key=key)
        return obj

    def get_meta_title(self, lang='en'):
        return getattr(self, f'meta_title_{lang}', '') or ''

    def get_meta_desc(self, lang='en'):
        return getattr(self, f'meta_desc_{lang}', '') or ''

    def get_og_title(self, lang='en'):
        return getattr(self, f'og_title_{lang}', '') or self.get_meta_title(lang)

    def get_og_desc(self, lang='en'):
        return getattr(self, f'og_desc_{lang}', '') or self.get_meta_desc(lang)

    def get_canonical_url(self):
        return self.canonical_url or ''

    def get_focus_keyword(self):
        return self.focus_keyword or ''

    def get_robots_meta(self):
        return 'noindex, follow' if self.noindex else 'index, follow'


# ── SlugHistory ───────────────────────────────────────────────────────────────

def _record_slug_change(instance, slug_fields=None):
    """
    Before a model save, record any slug that changed into SlugHistory
    so SlugRedirectMiddleware can issue 301 redirects from old URLs.

    slug_fields: dict of {language: field_name}.
        Defaults to detecting modeltranslation fields (slug_en, slug_tr, …)
        falling back to a plain 'slug' field.
    """
    if instance.pk is None:
        return

    if slug_fields is None:
        slug_fields = {}
        for suffix in ('en', 'tr'):
            fname = f'slug_{suffix}'
            if hasattr(instance, fname):
                slug_fields[suffix] = fname
        if not slug_fields and hasattr(instance, 'slug'):
            slug_fields = {'en': 'slug'}

    if not slug_fields:
        return

    try:
        old = instance.__class__._default_manager.get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return

    ct = ContentType.objects.get_for_model(instance)
    for lang, field in slug_fields.items():
        old_val = getattr(old, field, '') or ''
        new_val = getattr(instance, field, '') or ''
        if old_val and old_val != new_val:
            SlugHistory.objects.get_or_create(
                content_type=ct,
                object_id=instance.pk,
                old_slug=old_val,
                language=lang,
            )


class SlugHistory(models.Model):
    """Stores old slugs for 301 redirects."""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Content type')
    object_id = models.PositiveIntegerField(verbose_name='Object ID')
    content_object = GenericForeignKey('content_type', 'object_id')
    old_slug = models.SlugField(max_length=255, verbose_name='Old slug')
    language = models.CharField(max_length=5, default='en', verbose_name='Language')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Slug History'
        verbose_name_plural = 'Slug History'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.old_slug} → {self.content_object}'


# ── Webinar Landing (FA) ──────────────────────────────────────────────────────
# Isolated singleton model + registrations table for the Persian webinar
# landing page (UAE / Turkey audience). All fields are pre-filled with the
# default Persian copy so the page renders correctly even before an admin
# opens the change form.

class WebinarLandingSettings(_SingletonMixin):
    """Singleton model that powers the /webinar/ Persian landing page."""

    # ── Hero ─────────────────────────────────────────────────────────────────
    hero_badge = models.CharField(
        max_length=200,
        default='ویژه ایرانیان مقیم امارات و ترکیه',
        verbose_name='Hero Badge',
    )
    hero_title = models.CharField(
        max_length=300,
        default='وبینار تخصصی اقامت و سرمایه‌گذاری اروپا',
        verbose_name='Hero Title',
    )
    hero_subtitle = models.TextField(
        default='<p>اخذ اقامت دائم اروپا</p><p>برای سرمایه‌گذاران ایرانی</p>',
        verbose_name='Hero Subtitle',
        help_text='Large secondary heading. Each paragraph becomes a separate display line.',
    )
    hero_description = models.TextField(
        default=(
            '<p>اگر در امارات یا ترکیه زندگی می‌کنید و به دنبال یک مسیر مطمئن '
            'برای سرمایه‌گذاری، دریافت اقامت اروپا و ساخت آینده‌ای امن‌تر '
            'برای خانواده خود هستید، این وبینار برای شماست.</p>'
        ),
        verbose_name='Hero Description',
    )
    hero_background_image = models.ImageField(
        upload_to='webinar_landing/',
        blank=True,
        null=True,
        verbose_name='Hero Background Image',
        help_text='Cinematic Dubai skyline / sunset image. If empty, an elegant gradient is used.',
    )
    hero_speaker_photo = models.ImageField(
        upload_to='webinar_landing/speakers/',
        blank=True,
        null=True,
        verbose_name='Hero Speaker Photo',
        help_text=(
            'Portrait of the host/speaker. PNG with transparent background recommended '
            '(at least 800×1100 px). If empty, the bundled Dr. Meisam Sabour image is used.'
        ),
    )
    hero_speaker_name = models.CharField(
        max_length=200,
        default='MEISAM SABOUR | PhD',
        verbose_name='Hero Speaker Name',
        help_text='Shown in gold under the speaker photo. Latin script recommended.',
    )
    hero_speaker_title = models.CharField(
        max_length=200,
        default='هم‌مؤسس ADONIS',
        verbose_name='Hero Speaker Title',
        help_text='Short role/credential line under the speaker name.',
    )

    # ── Webinar info bar ────────────────────────────────────────────────────
    webinar_date_text = models.CharField(
        max_length=200,
        default='پنجشنبه — 21 May 2026 — 31 اردیبهشت 1405',
        verbose_name='Webinar Date Text',
    )
    webinar_time_text = models.CharField(
        max_length=160,
        default='ساعت ۲۰ — به وقت امارات',
        verbose_name='Webinar Time Text',
    )
    webinar_format_text = models.CharField(
        max_length=160,
        default='برگزاری آنلاین — ظرفیت محدود',
        verbose_name='Webinar Format Text',
    )

    # ── Benefits cards ──────────────────────────────────────────────────────
    benefit_1_title = models.CharField(max_length=160, default='اقامت دائم اروپا', verbose_name='Benefit 1 — Title')
    benefit_1_text = models.CharField(max_length=240, default='برای شما و خانواده', verbose_name='Benefit 1 — Subtitle')
    benefit_2_title = models.CharField(max_length=160, default='دسترسی به بازار اروپا', verbose_name='Benefit 2 — Title')
    benefit_2_text = models.CharField(max_length=240, default='و فرصت‌های بین‌المللی', verbose_name='Benefit 2 — Subtitle')
    benefit_3_title = models.CharField(max_length=160, default='فرصت‌های بیشتر', verbose_name='Benefit 3 — Title')
    benefit_3_text = models.CharField(max_length=240, default='برای سرمایه‌گذاری و رشد', verbose_name='Benefit 3 — Subtitle')

    # ── Intro video section ─────────────────────────────────────────────────
    intro_title = models.CharField(
        max_length=200,
        default='چرا این وبینار مهم است؟',
        verbose_name='Intro Section Title',
    )
    intro_description = models.TextField(
        default=(
            '<p>در این وبینار، به‌صورت شفاف درباره روش‌های دریافت اقامت اروپا، '
            'شرایط واقعی سرمایه‌گذاری در یونان، مزایا، ریسک‌ها و نکات مهم '
            'قبل از تصمیم‌گیری صحبت خواهیم کرد.</p>'
        ),
        verbose_name='Intro Section Description',
    )
    intro_video = models.FileField(
        upload_to='webinar_landing/',
        blank=True,
        null=True,
        verbose_name='Intro Video',
        help_text='Short MP4/WEBM intro. If empty, an elegant placeholder with an animated play button is shown.',
    )

    # ── Registration form ───────────────────────────────────────────────────
    form_title = models.CharField(max_length=200, default='ثبت‌نام در وبینار', verbose_name='Form Title')
    form_button_text = models.CharField(max_length=120, default='ثبت‌نام در وبینار', verbose_name='Form Button Text')

    # ── Success modal ───────────────────────────────────────────────────────
    success_title = models.CharField(
        max_length=200,
        default='ثبت‌نام شما با موفقیت انجام شد.',
        verbose_name='Success — Title',
    )
    success_text = models.TextField(
        default=(
            '<p>شما در وبینار تاریخ ۲۱ می ۲۰۲۶ ویژه اقامت و سرمایه‌گذاری اروپا '
            'ثبت‌نام شدید.</p>'
            '<p>اطلاعات و لینک ورود به وبینار برای شما ارسال خواهد شد.</p>'
        ),
        verbose_name='Success — Body',
    )
    success_button_text = models.CharField(max_length=80, default='متوجه شدم', verbose_name='Success — Button')

    # ── Final CTA ───────────────────────────────────────────────────────────
    cta_title = models.TextField(
        default='<p>ظرفیت این وبینار محدود است.</p><p>همین حالا ثبت‌نام کنید.</p>',
        verbose_name='Final CTA Title',
        help_text='Each paragraph becomes a separate display line. The second paragraph is shown in gold.',
    )
    cta_button_text = models.CharField(max_length=120, default='رزرو جایگاه در وبینار', verbose_name='Final CTA Button')

    # ── Activation & SEO ────────────────────────────────────────────────────
    active_status = models.BooleanField(
        default=True,
        verbose_name='Page Active',
        help_text='Uncheck to hide the /webinar/ page (returns 404).',
    )
    meta_title = models.CharField(
        max_length=180,
        blank=True,
        default='وبینار تخصصی اقامت و سرمایه‌گذاری اروپا',
        verbose_name='SEO Meta Title',
    )
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        default=(
            'وبینار تخصصی اقامت دائم اروپا و سرمایه‌گذاری در یونان '
            'ویژه ایرانیان مقیم امارات و ترکیه — ظرفیت محدود.'
        ),
        verbose_name='SEO Meta Description',
    )
    canonical_url = models.CharField(
        max_length=300,
        blank=True,
        default='',
        verbose_name='Canonical URL',
    )
    og_title = models.CharField(
        max_length=120,
        blank=True,
        default='',
        verbose_name='OG Title',
    )
    og_description = models.CharField(
        max_length=220,
        blank=True,
        default='',
        verbose_name='OG Description',
    )
    og_image = models.ImageField(
        upload_to='webinar_landing/og/',
        blank=True,
        null=True,
        verbose_name='OG Image',
    )
    focus_keyword = models.CharField(
        max_length=160,
        blank=True,
        default='',
        verbose_name='Focus Keyword',
    )
    noindex = models.BooleanField(
        default=False,
        verbose_name='Noindex',
    )
    seo_status = models.CharField(
        max_length=20,
        choices=SEO_STATUS_CHOICES,
        default='needs_review',
        verbose_name='SEO Status',
    )

    class Meta:
        verbose_name = 'Webinar Landing — Settings'
        verbose_name_plural = 'Webinar Landing — Settings'

    def __str__(self):
        return 'Webinar Landing Settings'


class WebinarRegistration(models.Model):
    """A single registration entered through the /webinar/ landing form."""

    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    phone = models.CharField(max_length=40, verbose_name='Phone Number')
    email = models.EmailField(max_length=200, verbose_name='Email')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Registered At')

    class Meta:
        verbose_name = 'Webinar Registration'
        verbose_name_plural = 'Webinar Registrations'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} — {self.phone}'

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.strip()


# ── Persian (fa) prototype hero settings ─────────────────────────────────────
# Singleton model used ONLY by /fa-new/ . Lets the team upload a dedicated
# cinematic hero video for the Persian preview page WITHOUT touching the
# English site's HeaderSettings.hero_video. Completely isolated:
#   • brand-new table (core_fanewsettings)
#   • no relations to any existing model
#   • only consumed by the fa_new_home view + templates/fa_new/home.html
class FaNewSettings(models.Model):
    """Singleton settings for the /fa-new/ Persian preview homepage.

    Controls: logo, hero video, 4 scroll overlay texts, CTA buttons, colors.
    PK is always forced to 1. Use FaNewSettings.get_settings() to access.
    Does not affect the English site or /fa/... ad pages.
    """

    # ── Media ──────────────────────────────────────────────────────────────────
    header_logo = models.ImageField(
        upload_to='fa-new/', blank=True, null=True,
        verbose_name='لوگو هدر',
        help_text='PNG با پس‌زمینه شفاف — ارتفاع ۶۰ تا ۱۲۰ پیکسل.',
    )
    hero_video = models.FileField(
        upload_to='fa-new/', blank=True, null=True,
        verbose_name='ویدیو هیرو',
        help_text='MP4 (H.264) با faststart — حداکثر ۵۰۰ مگابایت.',
    )
    hero_video_poster = models.ImageField(
        upload_to='fa-new/', blank=True, null=True,
        verbose_name='پوستر ویدیو',
        help_text='تصویر فریم اول که قبل از لود شدن ویدیو نشان داده می‌شود.',
    )

    # ── Hero Overlay Texts ─────────────────────────────────────────────────────
    hero_label = models.CharField(
        max_length=100, blank=True,
        verbose_name='لیبل طلایی بالای عنوان',
        help_text='متن کوچک طلایی که بالای عنوان اصلی نشان داده می‌شود. مثال: ADONIS · ATHENS',
    )
    hero_title = models.CharField(
        max_length=200, blank=True,
        verbose_name='عنوان اصلی هیرو',
        help_text='عنوان بزرگ که روی ویدیو نمایش داده می‌شود.',
    )
    hero_subtitle = models.CharField(
        max_length=300, blank=True,
        verbose_name='زیرعنوان هیرو',
        help_text='متن کوچک‌تر زیر عنوان اصلی.',
    )
    hero_cta_text = models.CharField(
        max_length=100, blank=True,
        verbose_name='متن دکمه CTA',
        help_text='متن دکمه اصلی روی هیرو. مثال: دریافت مشاوره رایگان',
    )
    hero_cta_url = models.CharField(
        max_length=200, blank=True,
        verbose_name='لینک دکمه CTA',
        help_text='آدرس لینک دکمه. مثال: #fa-section-consult',
    )

    # ── Overlay 1 ─────────────────────────────────────────────────────────────
    o1_eyebrow = models.CharField(
        max_length=100, blank=True, default='ADONIS · ATHENS',
        verbose_name='اسلاید ۱ — متن کوچک بالا',
    )
    o1_title = models.CharField(
        max_length=250, blank=True, default='سرمایه‌گذاری در یونان',
        verbose_name='اسلاید ۱ — عنوان اصلی',
        help_text='کلمه‌ای که باید طلایی شود را در فیلد «کلمه طلایی» بنویسید.',
    )
    o1_highlight = models.CharField(
        max_length=100, blank=True, default='یونان',
        verbose_name='اسلاید ۱ — کلمه طلایی',
        help_text='این کلمه باید دقیقاً در متن عنوان وجود داشته باشد.',
    )
    o1_subtitle = models.TextField(
        blank=True, default='آغاز یک مسیر مطمئن برای اقامت اروپا',
        verbose_name='اسلاید ۱ — زیرعنوان',
    )
    o1_start = models.FloatField(
        default=0, verbose_name='اسلاید ۱ — شروع (%)',
        help_text='درصد شروع نمایش این اسلاید در اسکرول (۰ تا ۱۰۰)',
    )
    o1_end = models.FloatField(
        default=30, verbose_name='اسلاید ۱ — پایان (%)',
        help_text='درصد پایان نمایش این اسلاید در اسکرول (۰ تا ۱۰۰)',
    )

    # ── Overlay 2 ─────────────────────────────────────────────────────────────
    o2_eyebrow = models.CharField(
        max_length=100, blank=True, default='خانه · آتن',
        verbose_name='اسلاید ۲ — متن کوچک بالا',
    )
    o2_title = models.CharField(
        max_length=250, blank=True, default='خانه‌ای در آتن، آینده‌ای در اروپا',
        verbose_name='اسلاید ۲ — عنوان اصلی',
    )
    o2_highlight = models.CharField(
        max_length=100, blank=True, default='اروپا',
        verbose_name='اسلاید ۲ — کلمه طلایی',
    )
    o2_subtitle = models.TextField(
        blank=True, default='خرید ملک، دریافت اقامت، ساختن یک زندگی جدید',
        verbose_name='اسلاید ۲ — زیرعنوان',
    )
    o2_start = models.FloatField(
        default=30, verbose_name='اسلاید ۲ — شروع (%)',
    )
    o2_end = models.FloatField(
        default=60, verbose_name='اسلاید ۲ — پایان (%)',
    )

    # ── Overlay 3 ─────────────────────────────────────────────────────────────
    o3_eyebrow = models.CharField(
        max_length=100, blank=True, default='خانواده · پوشش کامل',
        verbose_name='اسلاید ۳ — متن کوچک بالا',
    )
    o3_title = models.CharField(
        max_length=250, blank=True, default='اقامت یونان برای خانواده شما',
        verbose_name='اسلاید ۳ — عنوان اصلی',
    )
    o3_highlight = models.CharField(
        max_length=100, blank=True, default='خانواده شما',
        verbose_name='اسلاید ۳ — کلمه طلایی',
    )
    o3_subtitle = models.TextField(
        blank=True, default='همراه با همسر، فرزندان و والدین دو طرف',
        verbose_name='اسلاید ۳ — زیرعنوان',
    )
    o3_start = models.FloatField(
        default=60, verbose_name='اسلاید ۳ — شروع (%)',
    )
    o3_end = models.FloatField(
        default=85, verbose_name='اسلاید ۳ — پایان (%)',
    )

    # ── Overlay 4 (CTA slide) ─────────────────────────────────────────────────
    o4_eyebrow = models.CharField(
        max_length=100, blank=True, default='گام بعدی',
        verbose_name='اسلاید ۴ — متن کوچک بالا',
    )
    o4_title = models.CharField(
        max_length=250, blank=True, default='با ADONIS قدم بعدی را بردارید',
        verbose_name='اسلاید ۴ — عنوان اصلی',
    )
    o4_highlight = models.CharField(
        max_length=100, blank=True, default='ADONIS',
        verbose_name='اسلاید ۴ — کلمه طلایی',
    )
    o4_start = models.FloatField(
        default=85, verbose_name='اسلاید ۴ — شروع (%)',
    )
    o4_end = models.FloatField(
        default=101, verbose_name='اسلاید ۴ — پایان (%)',
        help_text='مقدار بیش از ۱۰۰ یعنی تا انتهای اسکرول نشان داده می‌شود.',
    )

    # ── CTA Buttons ───────────────────────────────────────────────────────────
    cta_primary_label = models.CharField(
        max_length=80, blank=True, default='دریافت مشاوره',
        verbose_name='دکمه اول — متن',
    )
    cta_primary_url = models.CharField(
        max_length=300, blank=True, default='#fa-section-consult',
        verbose_name='دکمه اول — لینک',
    )
    cta_secondary_label = models.CharField(
        max_length=80, blank=True, default='مشاهده پروژه‌ها',
        verbose_name='دکمه دوم — متن',
    )
    cta_secondary_url = models.CharField(
        max_length=300, blank=True, default='#fa-section-projects',
        verbose_name='دکمه دوم — لینک',
    )

    # ── Hero Colors ───────────────────────────────────────────────────────────
    hero_text_color = models.CharField(
        max_length=30, blank=True, default='#ffffff',
        verbose_name='رنگ عنوان‌ها',
        help_text='رنگ H1/H2 روی هیرو. فرمت hex (#rrggbb).',
    )
    hero_subtitle_color = models.CharField(
        max_length=30, blank=True, default='#cccccc',
        verbose_name='رنگ زیرعنوان‌ها',
    )
    hero_accent_color = models.CharField(
        max_length=30, blank=True, default='#efd99a',
        verbose_name='رنگ لهجه (طلایی)',
        help_text='رنگ کلمه طلایی در عنوان‌ها.',
    )
    hero_scrim_color = models.CharField(
        max_length=30, blank=True, default='#060814',
        verbose_name='رنگ پس‌زمینه تیره‌کننده (scrim)',
        help_text='رنگ لایه تیره روی ویدیو. معمولاً همرنگ پس‌زمینه سایت.',
    )
    hero_cta_primary_bg = models.CharField(
        max_length=30, blank=True, default='#efd99a',
        verbose_name='دکمه اول — رنگ پس‌زمینه',
    )
    hero_cta_primary_text = models.CharField(
        max_length=30, blank=True, default='#1b1306',
        verbose_name='دکمه اول — رنگ متن',
    )
    hero_cta_secondary_border = models.CharField(
        max_length=30, blank=True, default='#808080',
        verbose_name='دکمه دوم — رنگ حاشیه',
    )
    hero_cta_secondary_text = models.CharField(
        max_length=30, blank=True, default='#ffffff',
        verbose_name='دکمه دوم — رنگ متن',
    )

    # ── Hero Position & Font Sizes ──────────────────────────────────────────────
    VERTICAL_POSITION_CHOICES = [
        ('top', 'بالا'),
        ('center', 'وسط'),
        ('bottom', 'پایین'),
    ]
    hero_content_vertical_position = models.CharField(
        max_length=12, blank=True, default='center',
        choices=VERTICAL_POSITION_CHOICES,
        verbose_name='جایگاه عمودی محتوای هیرو',
        help_text='تعیین می‌کند عنوان و زیرعنوان در کجای صفحه هیرو قرار بگیرند.',
    )
    hero_title_font_size = models.CharField(
        max_length=10, blank=True, default='48px',
        verbose_name='اندازه فونت عنوان هیرو',
        help_text='مثال: 48px, 56px, 64px — مقدار پیش‌فرض: 48px',
    )
    hero_subtitle_font_size = models.CharField(
        max_length=10, blank=True, default='18px',
        verbose_name='اندازه فونت زیرعنوان هیرو',
        help_text='مثال: 16px, 18px, 20px — مقدار پیش‌فرض: 18px',
    )

    # ── Meta ──────────────────────────────────────────────────────────────────
    note = models.CharField(
        max_length=200, blank=True,
        verbose_name='یادداشت داخلی',
        help_text='فقط برای ادمین — روی سایت نمایش داده نمی‌شود.',
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = '/fa-new/ — تنظیمات پیش‌نمایش فارسی'
        verbose_name_plural = '/fa-new/ — تنظیمات پیش‌نمایش فارسی'

    def __str__(self):
        return '/fa-new/ Persian Preview Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ── /fa-new/ Featured Properties (5 slots for homepage carousel) ──────────────
# Singleton model that holds 5 property slots for the Persian homepage carousel.
# Admin can select exactly 5 properties that will show in the carousel.
# Uses FaProperty (Persian properties) - NOT the English properties.Property model.

class FaNewFeaturedProperties(models.Model):
    """Singleton settings for 5 featured properties on the /fa-new/ Persian homepage carousel.
    
    Uses the FaProperty model (from persian_cms app) which is completely separate from
    the English properties.Property model. Admin can explicitly select 5 properties
    that will appear in the carousel on the Persian landing page.
    PK is always forced to 1. Use FaNewFeaturedProperties.get_settings() to access.
    """
    
    property_1 = models.ForeignKey(
        'persian_cms.FaProperty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_slot_1',
        verbose_name='ملک منتخب ۱',
        help_text='اولین ملک در کاروسل صفحه اصلی فارسی',
    )
    property_2 = models.ForeignKey(
        'persian_cms.FaProperty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_slot_2',
        verbose_name='ملک منتخب ۲',
        help_text='دومین ملک در کاروسل صفحه اصلی فارسی',
    )
    property_3 = models.ForeignKey(
        'persian_cms.FaProperty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_slot_3',
        verbose_name='ملک منتخب ۳',
        help_text='سومین ملک در کاروسل صفحه اصلی فارسی',
    )
    property_4 = models.ForeignKey(
        'persian_cms.FaProperty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_slot_4',
        verbose_name='ملک منتخب ۴',
        help_text='چهارمین ملک در کاروسل صفحه اصلی فارسی',
    )
    property_5 = models.ForeignKey(
        'persian_cms.FaProperty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='featured_slot_5',
        verbose_name='ملک منتخب ۵',
        help_text='پنجمین ملک در کاروسل صفحه اصلی فارسی',
    )
    
    class Meta:
        verbose_name = 'املاک منتخب کاروسل'
        verbose_name_plural = 'املاک منتخب کاروسل'
    
    def __str__(self):
        return 'تنظیمات املاک منتخب کاروسل'
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
    
    def get_properties_list(self):
        """Return list of selected properties in order (non-null only)."""
        props = []
        for i in range(1, 6):
            p = getattr(self, f'property_{i}', None)
            if p is not None:
                props.append(p)
        return props


# ── /fa-new/ Hero slides ──────────────────────────────────────────────────────
# Each row is one "scene" that appears during the scroll-driven hero animation.

class FaNewHeroSlide(models.Model):
    """One text scene in the /fa-new/ hero scroll animation.

    Scenes are shown in `order` sequence. The JS scroll driver positions them
    using data-start / data-end attributes (scroll progress 0–10 scale).
    """

    settings = models.ForeignKey(
        'FaNewSettings', on_delete=models.CASCADE,
        related_name='hero_slides', verbose_name='تنظیمات',
    )
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')

    eyebrow = models.CharField(
        max_length=100, blank=True,
        verbose_name='متن کوچک بالای عنوان',
        help_text='مثال: ADONIS · ATHENS  یا  خانه · آتن',
    )
    headline = models.CharField(
        max_length=250,
        verbose_name='عنوان اصلی',
        help_text='متن کامل عنوان. کلمه‌ای که می‌خواهی طلایی شود را در فیلد بعدی بنویس.',
    )
    headline_highlight = models.CharField(
        max_length=100, blank=True,
        verbose_name='کلمه طلایی در عنوان',
        help_text='این کلمه با رنگ طلایی نشان داده می‌شود. باید دقیقاً با متن عنوان یکسان باشد.',
    )
    subtitle = models.CharField(
        max_length=250, blank=True,
        verbose_name='زیرعنوان',
        help_text='متن کوچک‌تر زیر عنوان اصلی. برای اسلاید آخر (CTA) خالی بگذارید.',
    )

    is_cta = models.BooleanField(
        default=False,
        verbose_name='اسلاید CTA (دکمه‌دار)؟',
        help_text='فعال کن اگر این اسلاید آخر است و دو دکمه دارد.',
    )
    cta_primary_label = models.CharField(
        max_length=80, blank=True, default='دریافت مشاوره',
        verbose_name='متن دکمه اول',
    )
    cta_primary_url = models.CharField(
        max_length=300, blank=True, default='#fa-section-consult',
        verbose_name='لینک دکمه اول',
    )
    cta_secondary_label = models.CharField(
        max_length=80, blank=True, default='مشاهده پروژه‌ها',
        verbose_name='متن دکمه دوم',
    )
    cta_secondary_url = models.CharField(
        max_length=300, blank=True, default='#fa-section-projects',
        verbose_name='لینک دکمه دوم',
    )

    start_time = models.FloatField(
        default=0.0,
        verbose_name='شروع (scroll scale 0–10)',
        help_text='زمان شروع نمایش این اسلاید در انیمیشن اسکرول (مقیاس ۰ تا ۱۰)',
    )
    end_time = models.FloatField(
        default=3.0,
        verbose_name='پایان (scroll scale 0–10)',
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'اسلاید هیرو'
        verbose_name_plural = 'اسلایدهای هیرو'

    def __str__(self):
        return f'{self.order}. {self.headline[:60]}'


# ── /fa-new/ Section builder ───────────────────────────────────────────────────
# Each row is one content section on the /fa-new/ Persian page.
# Sections are rendered in `order` sequence; inactive ones are skipped.

class FaNewSection(models.Model):
    SECTION_TYPES = [
        ('why_greece', 'مزایای کلیدی یونان'),
        ('why_adonis', 'آشنایی با آدونیس'),
        ('why_adonis_stats', 'چرا آدونیس؟ (آمار)'),
        ('intro_stats', 'آشنایی با آدونیس (قدیمی)'),
        ('services', 'خدمات آدونیس'),
        ('routes', 'مسیرهای گلدن ویزا'),
        ('projects', 'پروژه‌های منتخب'),
        ('process', 'فرآیند همکاری'),
        ('trust', 'اعتماد و تجربه'),
        ('consult', 'مشاوره رایگان'),
        ('gateway', 'معرفی خدمات آدونیس'),
        ('residency_types', 'انواع اقامت یونان (۳ کارت لاکچری)'),
        ('featured_properties', 'پروژه‌های منتخب املاک (کاروسل)'),
    ]
    MOBILE_LAYOUT_CHOICES = [
        ('stacked', 'stacked'),
        ('carousel', 'carousel'),
    ]
    DESKTOP_LAYOUT_CHOICES = [
        ('two_columns', '2 columns'),
        ('three_columns', '3 columns'),
        ('full_width', 'full width'),
    ]
    TEXT_ALIGNMENT_CHOICES = [
        ('right', 'right'),
        ('center', 'center'),
        ('left', 'left'),
        ('justify', 'justify'),
    ]
    FONT_WEIGHT_CHOICES = [
        ('300', '300'),
        ('400', '400'),
        ('500', '500'),
        ('600', '600'),
        ('700', '700'),
        ('800', '800'),
        ('900', '900'),
    ]

    # ── 1) General ───────────────────────────────────────────────────────────
    section_name = models.CharField(
        max_length=140,
        blank=True,
        verbose_name='نام سکشن',
        help_text='نام مدیریتی سکشن در پنل ادمین.',
    )
    section_type = models.CharField(
        max_length=20, choices=SECTION_TYPES,
        verbose_name='نوع بخش',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
        help_text='غیرفعال کردن این بخش را از صفحه پنهان می‌کند.',
    )
    order = models.PositiveIntegerField(
        default=0, db_index=True,
        verbose_name='ترتیب نمایش',
        help_text='عدد کوچک‌تر = بالاتر در صفحه',
    )
    anchor_id = models.SlugField(
        max_length=80,
        blank=True,
        verbose_name='anchor id',
        help_text='شناسه یکتا برای لینک‌دهی داخل صفحه. مثال: fa-section-gateway',
    )
    show_on_desktop = models.BooleanField(default=True, verbose_name='نمایش در دسکتاپ')
    show_on_mobile = models.BooleanField(default=True, verbose_name='نمایش در موبایل')

    # ── 2) Texts ─────────────────────────────────────────────────────────────
    eyebrow = models.CharField(
        max_length=100, blank=True,
        verbose_name='eyebrow',
        help_text='برچسب کوچک بالای تیتر',
    )
    title = models.CharField(
        max_length=250, blank=True,
        verbose_name='title',
    )
    subtitle = models.TextField(
        blank=True,
        verbose_name='subtitle',
        help_text='زیرتیتر',
    )
    description = models.TextField(
        blank=True,
        verbose_name='description',
        help_text='توضیح اصلی سکشن',
    )
    cta_primary_text = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='متن CTA اول',
    )
    cta_primary_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='لینک CTA اول',
    )
    cta_secondary_text = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='متن CTA دوم',
    )
    cta_secondary_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='لینک CTA دوم',
    )

    # ── 3) Images / Video ────────────────────────────────────────────────────
    background_image = models.ImageField(
        upload_to='fa-new/sections/backgrounds/',
        blank=True,
        null=True,
        verbose_name='تصویر پس‌زمینه',
    )
    background_image_alt = models.CharField(
        max_length=220,
        blank=True,
        verbose_name='alt تصویر پس‌زمینه',
    )
    background_image_opacity = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='شفافیت تصویر پس‌زمینه (%)',
        help_text='۰ = کاملاً پنهان · ۱۰۰ = کاملاً نمایان. پیشنهاد: ۳۰ تا ۷۰',
    )
    BACKGROUND_POSITION_CHOICES = [
        ('center center', 'مرکز وسط (پیش‌فرض)'),
        ('center top', 'بالا - مرکز'),
        ('center bottom', 'پایین - مرکز'),
        ('right center', 'مرکز - راست'),
        ('left center', 'مرکز - چپ'),
    ]
    background_image_position = models.CharField(
        max_length=30,
        choices=BACKGROUND_POSITION_CHOICES,
        default='center center',
        blank=True,
        verbose_name='موقعیت تصویر پس‌زمینه',
        help_text='کنترل می‌کند کدام بخش از تصویر در مرکز نمایش باشد. برای تصاویر عمودی «بالا - مرکز» مناسب است.',
    )
    background_video = models.FileField(
        upload_to='fa-new/sections/videos/',
        blank=True,
        null=True,
        verbose_name='ویدیو پس‌زمینه',
    )
    card_image_1 = models.ImageField(
        upload_to='fa-new/sections/cards/',
        blank=True,
        null=True,
        verbose_name='تصویر کارت اول',
    )
    card_image_1_alt = models.CharField(
        max_length=220,
        blank=True,
        verbose_name='alt تصویر کارت اول',
    )
    card_image_2 = models.ImageField(
        upload_to='fa-new/sections/cards/',
        blank=True,
        null=True,
        verbose_name='تصویر کارت دوم',
    )
    card_image_2_alt = models.CharField(
        max_length=220,
        blank=True,
        verbose_name='alt تصویر کارت دوم',
    )

    # ── 4) Two-card gateway content ──────────────────────────────────────────
    card_1_label = models.CharField(max_length=120, blank=True, verbose_name='Card 1 label')
    card_1_title = models.CharField(max_length=220, blank=True, verbose_name='Card 1 title')
    card_1_subtitle = models.CharField(max_length=260, blank=True, verbose_name='Card 1 subtitle')
    card_1_description = models.TextField(blank=True, verbose_name='Card 1 description')
    card_1_image = models.ImageField(
        upload_to='fa-new/sections/cards/',
        blank=True,
        null=True,
        verbose_name='Card 1 image',
    )
    card_1_image_alt = models.CharField(max_length=220, blank=True, verbose_name='Card 1 image alt')
    card_1_cta_text = models.CharField(max_length=120, blank=True, verbose_name='Card 1 CTA text')
    card_1_cta_link = models.CharField(max_length=500, blank=True, verbose_name='Card 1 CTA link')
    card_1_accent_color = models.CharField(
        max_length=30, blank=True, default='#1E5AA8', verbose_name='Card 1 accent color'
    )

    card_2_label = models.CharField(max_length=120, blank=True, verbose_name='Card 2 label')
    card_2_title = models.CharField(max_length=220, blank=True, verbose_name='Card 2 title')
    card_2_subtitle = models.CharField(max_length=260, blank=True, verbose_name='Card 2 subtitle')
    card_2_description = models.TextField(blank=True, verbose_name='Card 2 description')
    card_2_image = models.ImageField(
        upload_to='fa-new/sections/cards/',
        blank=True,
        null=True,
        verbose_name='Card 2 image',
    )
    card_2_image_alt = models.CharField(max_length=220, blank=True, verbose_name='Card 2 image alt')
    card_2_cta_text = models.CharField(max_length=120, blank=True, verbose_name='Card 2 CTA text')
    card_2_cta_link = models.CharField(max_length=500, blank=True, verbose_name='Card 2 CTA link')
    card_2_accent_color = models.CharField(
        max_length=30, blank=True, default='#1E5AA8', verbose_name='Card 2 accent color'
    )

    # ── 5) Design ────────────────────────────────────────────────────────────
    background_color = models.CharField(max_length=30, blank=True, default='#071527', verbose_name='background color')
    gradient_color = models.CharField(max_length=30, blank=True, default='transparent', verbose_name='gradient color')
    text_color = models.CharField(max_length=30, blank=True, default='#FFFFFF', verbose_name='text color')
    title_color = models.CharField(max_length=30, blank=True, default='#0B1F3A', verbose_name='رنگ عنوان', help_text='رنگ عنوان اصلی سکشن (مثال: #0B1F3A برای سرمه‌ای)')
    accent_color = models.CharField(max_length=30, blank=True, default='#1E5AA8', verbose_name='accent color')
    card_background = models.CharField(max_length=30, blank=True, default='#FFFFFF', verbose_name='card background')
    border_color = models.CharField(max_length=30, blank=True, default='rgba(11,31,58,0.1)', verbose_name='border color')
    border_radius = models.PositiveIntegerField(default=24, verbose_name='border radius')
    shadow_intensity = models.PositiveIntegerField(
        default=16,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='shadow intensity',
    )
    blur_intensity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        verbose_name='blur intensity',
    )
    section_padding_top = models.PositiveIntegerField(default=96, verbose_name='section padding top')
    section_padding_bottom = models.PositiveIntegerField(default=96, verbose_name='section padding bottom')
    card_gap = models.PositiveIntegerField(default=24, verbose_name='card gap')

    # ── 6) Typography ────────────────────────────────────────────────────────
    title_font_size_desktop = models.PositiveIntegerField(default=42, verbose_name='title font size desktop')
    title_font_size_mobile = models.PositiveIntegerField(default=30, verbose_name='title font size mobile')
    subtitle_font_size = models.PositiveIntegerField(default=22, verbose_name='subtitle font size')
    description_font_size = models.PositiveIntegerField(default=16, verbose_name='description font size')
    font_weight = models.CharField(
        max_length=3,
        choices=FONT_WEIGHT_CHOICES,
        default='700',
        verbose_name='font weight',
    )
    line_height = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.70,
        validators=[MinValueValidator(1.00), MaxValueValidator(3.00)],
        verbose_name='line height',
    )
    text_alignment = models.CharField(
        max_length=10,
        choices=TEXT_ALIGNMENT_CHOICES,
        default='center',
        verbose_name='تراز عنوان',
    )
    subtitle_alignment = models.CharField(
        max_length=10,
        choices=TEXT_ALIGNMENT_CHOICES,
        default='center',
        verbose_name='تراز زیرعنوان',
    )

    # ── 7) Responsive ────────────────────────────────────────────────────────
    mobile_layout = models.CharField(
        max_length=20,
        choices=MOBILE_LAYOUT_CHOICES,
        default='stacked',
        verbose_name='mobile layout',
    )
    desktop_layout = models.CharField(
        max_length=20,
        choices=DESKTOP_LAYOUT_CHOICES,
        default='two_columns',
        verbose_name='desktop layout',
    )
    max_width_container = models.PositiveIntegerField(default=1240, verbose_name='max width container')
    hide_image_on_mobile = models.BooleanField(default=False, verbose_name='hide image on mobile')

    # ── 8) Decorative transition (Hero -> Gateway) ─────────────────────────
    decorative_flowers_enabled = models.BooleanField(
        default=False,
        verbose_name='فعال‌سازی لایه تزئینی گل‌ها',
        help_text='لایه تزئینی بین Hero و Gateway. فقط برای حس بصری لوکس؛ محتوایی نیست.',
    )
    decorative_left_image = models.ImageField(
        upload_to='fa-new/decorative/',
        blank=True,
        null=True,
        verbose_name='تصویر گل سمت چپ',
        help_text='ترجیحاً WebP شفاف با شاخه گل کاغذی صورتی.',
    )
    decorative_right_image = models.ImageField(
        upload_to='fa-new/decorative/',
        blank=True,
        null=True,
        verbose_name='تصویر گل سمت راست',
        help_text='نسخه سبک‌تر سمت راست. ترجیحاً WebP شفاف.',
    )
    decorative_opacity = models.PositiveIntegerField(
        default=65,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='شفافیت لایه گل (%)',
        help_text='برای حس سینمایی subtle معمولاً بازه ۵۵ تا ۷۵ مناسب است.',
    )
    decorative_blur_intensity = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name='میزان blur لبه‌ها',
    )
    decorative_animation_enabled = models.BooleanField(
        default=True,
        verbose_name='فعال‌سازی حرکت آهسته گل‌ها',
    )
    decorative_show_on_mobile = models.BooleanField(
        default=False,
        verbose_name='نمایش تزئینات در موبایل',
        help_text='اگر خاموش باشد، در موبایل لایه تزئینی کامل مخفی می‌شود.',
    )

    # ── 11) Why Adonis Stats specific fields ──────────────────────────────────
    stats_use_persian_numbers = models.BooleanField(
        default=True,
        verbose_name='اعداد فارسی',
        help_text='اعداد آماری را به صورت فارسی (۰۱۲۳۴۵۶۷۸۹) نمایش بده',
    )
    stats_number_font_size = models.PositiveIntegerField(
        default=56,
        validators=[MinValueValidator(20), MaxValueValidator(120)],
        verbose_name='سایز عدد (px)',
        help_text='سایز فونت اعداد آماری در دسکتاپ. پیشنهاد: ۴۸ تا ۷۲ پیکسل',
    )
    stats_number_font_size_mobile = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(16), MaxValueValidator(80)],
        verbose_name='سایز عدد موبایل (px)',
        help_text='سایز فونت اعداد آماری در موبایل. پیشنهاد: ۳۲ تا ۴۸ پیکسل',
    )
    stats_number_color = models.CharField(
        max_length=30,
        blank=True,
        default='#D4B057',
        verbose_name='رنگ اعداد',
        help_text='رنگ اعداد آماری. پیش‌فرض: طلایی (#D4B057)',
    )
    stats_suffix_font_size = models.PositiveIntegerField(
        default=32,
        validators=[MinValueValidator(12), MaxValueValidator(60)],
        verbose_name='سایز پسوند (+)',
        help_text='سایز فونت پسوند (مثل +) در دسکتاپ',
    )
    stats_card_title_font_size = models.PositiveIntegerField(
        default=16,
        validators=[MinValueValidator(12), MaxValueValidator(32)],
        verbose_name='سایز عنوان کارت',
        help_text='سایز فونت عنوان زیر هر عدد (مثلاً «سال سابقه»)',
    )
    stats_animation_duration = models.PositiveIntegerField(
        default=2000,
        validators=[MinValueValidator(500), MaxValueValidator(5000)],
        verbose_name='مدت انیمیشن (ms)',
        help_text='مدت زمان انیمیشن شمارش اعداد به میلی‌ثانیه',
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'سکشن صفحه اصلی فارسی'
        verbose_name_plural = 'سکشن‌های صفحه اصلی'

    def __str__(self):
        label = self.get_section_type_display()
        name = self.section_name or self.title or '(بدون عنوان)'
        return f'{self.order}. {label} — {name}'

    def save(self, *args, **kwargs):
        if not self.section_name:
            self.section_name = self.get_section_type_display()
        if not self.anchor_id:
            base = self.section_name or self.section_type
            slug = slugify(base).replace('_', '-')
            fallback = f'fa-section-{self.section_type}'.replace('_', '-')
            self.anchor_id = (slug or fallback)[:80]
        super().save(*args, **kwargs)

    @property
    def resolved_anchor_id(self):
        if self.anchor_id:
            return self.anchor_id
        return f'fa-section-{self.section_type}'.replace('_', '-')

    @property
    def section_css_class(self):
        return f'adonis-fa-new-{self.section_type.replace("_", "-")}'

    @property
    def desktop_layout_class(self):
        mapping = {
            'two_columns': 'adonis-fa-new-layout-2',
            'three_columns': 'adonis-fa-new-layout-3',
            'full_width': 'adonis-fa-new-layout-1',
        }
        return mapping.get(self.desktop_layout, 'adonis-fa-new-layout-2')

    @property
    def mobile_layout_class(self):
        if self.mobile_layout == 'carousel':
            return 'adonis-fa-new-mobile-carousel'
        return 'adonis-fa-new-mobile-stacked'

    @property
    def has_two_card_content(self):
        if self.pk and self.gateway_cards.filter(is_active=True).exists():
            return True
        if self.section_type == 'gateway':
            return True
        return any([
            self.card_1_title, self.card_1_description, self.card_1_cta_text, self.card_1_image,
            self.card_2_title, self.card_2_description, self.card_2_cta_text, self.card_2_image,
            self.card_image_1, self.card_image_2,
        ])

    @property
    def active_gateway_cards(self):
        if not self.pk:
            return []
        prefetched = getattr(self, '_prefetched_objects_cache', {})
        if 'gateway_cards' in prefetched:
            return sorted(
                [card for card in prefetched['gateway_cards'] if card.is_active],
                key=lambda card: (card.order, card.id),
            )
        return self.gateway_cards.filter(is_active=True).order_by('order', 'id')

    @property
    def section_inline_style(self):
        shadow_alpha = max(0, min(self.shadow_intensity, 100)) / 100
        blur_px = max(0, min(self.blur_intensity, 40))
        bg_opacity = max(0, min(self.background_image_opacity, 100)) / 100
        bg_position = self.background_image_position
        style_tokens = [
            f'--fa-section-bg:{self.background_color or "#071527"}',
            f'--fa-section-gradient:{self.gradient_color or "transparent"}',
            f'--fa-section-text:{self.text_color or "#FFFFFF"}',
            f'--fa-section-accent:{self.accent_color or "#1E5AA8"}',
            f'--fa-section-card-bg:{self.card_background or "#FFFFFF"}',
            f'--fa-section-border:{self.border_color or "rgba(11,31,58,0.1)"}',
            f'--fa-section-radius:{self.border_radius or 24}px',
            f'--fa-section-shadow:0 16px 42px rgba(11,31,58,{shadow_alpha:.2f})',
            f'--fa-section-blur:{blur_px}px',
            f'--fa-section-pad-top:{self.section_padding_top or 96}px',
            f'--fa-section-pad-bottom:{self.section_padding_bottom or 96}px',
            f'--fa-section-gap:{self.card_gap or 24}px',
            f'--fa-section-title-desktop:{self.title_font_size_desktop or 42}px',
            f'--fa-section-title-mobile:{self.title_font_size_mobile or 30}px',
            f'--fa-section-subtitle-size:{self.subtitle_font_size or 22}px',
            f'--fa-section-description-size:{self.description_font_size or 16}px',
            f'--fa-section-font-weight:{self.font_weight or "700"}',
            f'--fa-section-line-height:{self.line_height or 1.70}',
            f'--fa-section-align:{self.text_alignment or "center"}',
            f'--fa-section-container-max:{self.max_width_container or 1240}px',
            f'--fa-section-bg-opacity:{bg_opacity:.2f}',
        ]
        if bg_position:
            style_tokens.append(f'--fa-section-bg-position:{bg_position}')
        if self.background_image:
            try:
                style_tokens.append(f'--fa-section-bg-image:url({self.background_image.url})')
            except Exception:
                pass
        return ';'.join(style_tokens)

    @property
    def admin_preview_url(self):
        return f'/#{self.resolved_anchor_id}'

    @property
    def card_1_inline_style(self):
        return f'--fa-gateway-accent:{self.card_1_accent_color or self.accent_color or "#1E5AA8"}'

    @property
    def card_2_inline_style(self):
        return f'--fa-gateway-accent:{self.card_2_accent_color or self.accent_color or "#1E5AA8"}'

    @property
    def decorative_inline_style(self):
        opacity = max(0, min(self.decorative_opacity or 0, 100)) / 100
        blur_px = max(0, min(self.decorative_blur_intensity or 0, 20))
        return ';'.join([
            f'--fa-transition-opacity:{opacity:.2f}',
            f'--fa-transition-blur:{blur_px}px',
        ])


class FaNewSectionItem(models.Model):
    """Generic item that lives inside a FaNewSection.

    Which fields are relevant depends on the parent section_type:
      why_greece  → badge (num), title, body
      why_adonis  → two sub-types distinguished by stat_number:
                     if stat_number set  → stat card  (stat_number, body as label)
                     if stat_number empty → bullet     (body)
      routes      → badge (tag), title, amount, body (newline-separated features),
                     is_featured, cta_label, cta_url
      projects    → badge (status), title, location, body, image, cta_label, cta_url
      process     → badge (step number), title, body
      trust       → body (quote), author_name, author_meta
      consult     → cta_label, cta_url  (one item per button)
    """

    section = models.ForeignKey(
        FaNewSection, on_delete=models.CASCADE,
        related_name='items', verbose_name='بخش',
    )
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')

    title = models.CharField(max_length=200, blank=True, verbose_name='عنوان')
    subtitle = models.CharField(max_length=240, blank=True, verbose_name='زیرعنوان')
    description = models.TextField(blank=True, verbose_name='توضیح')
    body = models.TextField(
        blank=True, verbose_name='متن / توضیح',
        help_text=(
            'برای مسیرهای گلدن ویزا: هر ویژگی را در یک خط بنویسید. '
            'برای نقل‌قول: متن کامل نقل‌قول را اینجا بنویسید.'
        ),
    )
    badge = models.CharField(
        max_length=50, blank=True,
        verbose_name='برچسب / شماره',
        help_text='ویژگی: ۰۱، ۰۲ … | مسیر: پایه، پریمیوم | فرآیند: ۱، ۲ …',
    )
    amount = models.CharField(
        max_length=100, blank=True,
        verbose_name='مبلغ',
        help_text='فقط برای مسیرهای گلدن ویزا، مثال: از ۲۵۰٬۰۰۰ یورو',
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='پیشنهاد ویژه؟',
        help_text='فقط برای مسیرها — کارت را برجسته (طلایی) می‌کند',
    )
    stat_number = models.CharField(
        max_length=20, blank=True,
        verbose_name='عدد آمار',
        help_text='فقط برای بخش «چرا آدونیس؟» — مثال: ۱۲+  یا  ۹۸٪',
    )
    author_name = models.CharField(
        max_length=100, blank=True,
        verbose_name='نام گوینده',
        help_text='فقط برای نقل‌قول‌ها',
    )
    author_meta = models.CharField(
        max_length=200, blank=True,
        verbose_name='اطلاعات تکمیلی گوینده',
        help_text='مثال: تهران → آتن، ۱۴۰۲',
    )
    location = models.CharField(
        max_length=100, blank=True,
        verbose_name='موقعیت',
        help_text='فقط برای پروژه‌ها — مثال: آلیموس · آتن',
    )
    image = models.ImageField(
        upload_to='fa-new/sections/',
        blank=True, null=True,
        verbose_name='تصویر',
        help_text='برای پروژه‌ها و کارت‌های اقامت (مسیرها/انواع اقامت)',
    )
    image_alt = models.CharField(
        max_length=220,
        blank=True,
        verbose_name='alt تصویر',
    )
    accent_color = models.CharField(
        max_length=30,
        blank=True,
        default='#1E5AA8',
        verbose_name='رنگ accent',
    )
    cta_label = models.CharField(
        max_length=100, blank=True,
        verbose_name='متن دکمه',
    )
    cta_url = models.CharField(
        max_length=500, blank=True,
        verbose_name='لینک دکمه',
        help_text='آدرس لینک یا anchor مثل #adonis-fa-new-consult',
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'آیتم'
        verbose_name_plural = 'آیتم‌ها'

    def __str__(self):
        return self.title or self.subtitle or self.body[:50] or f'آیتم {self.order}'

    @property
    def effective_description(self):
        return self.description or self.body


# ── /fa-new/ Gateway cards (repeater for section_type='gateway') ─────────────

class FaNewGatewayCard(models.Model):
    section = models.ForeignKey(
        FaNewSection,
        on_delete=models.CASCADE,
        related_name='gateway_cards',
        verbose_name='سکشن',
        help_text='این کارت فقط برای سکشن «بخش مسیرهای سرمایه‌گذاری» استفاده می‌شود.',
    )
    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name='ترتیب نمایش',
        help_text='عدد کوچک‌تر = نمایش زودتر',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
        help_text='در صورت غیرفعال بودن کارت در فرانت نمایش داده نمی‌شود.',
    )

    badge = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='برچسب کارت',
        help_text='مثال: ADONIS DEVELOPMENTS یا GOLDEN VISA',
    )
    title = models.CharField(
        max_length=220,
        blank=True,
        verbose_name='عنوان کارت',
    )
    subtitle = models.CharField(
        max_length=260,
        blank=True,
        verbose_name='زیرعنوان کارت',
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیح کارت',
    )

    image = models.ImageField(
        upload_to='fa-new/sections/cards/',
        blank=True,
        null=True,
        verbose_name='تصویر کارت',
    )
    image_alt = models.CharField(
        max_length=220,
        blank=True,
        verbose_name='alt تصویر کارت',
    )

    cta_text = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='متن CTA',
    )
    cta_link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='لینک CTA',
    )

    overlay_color = models.CharField(
        max_length=30,
        blank=True,
        default='transparent',
        verbose_name='رنگ overlay کارت',
        help_text='مثال: rgba(11,31,58,0.28) یا #1E5AA8 یا transparent',
    )
    overlay_opacity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='شفافیت overlay (%)',
    )
    accent_color = models.CharField(
        max_length=30,
        blank=True,
        default='#1E5AA8',
        verbose_name='رنگ accent کارت',
    )
    hover_preset = models.CharField(
        max_length=50,
        blank=True,
        default='default',
        verbose_name='پریست hover (آینده)',
        help_text='رزرو برای استایل hover در نسخه‌های بعدی.',
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'کارت مسیر سرمایه‌گذاری'
        verbose_name_plural = 'کارت‌های مسیر سرمایه‌گذاری'

    def __str__(self):
        title = self.title or self.badge or 'کارت'
        return f'{self.order}. {title}'

    @property
    def card_inline_style(self):
        accent = self.accent_color or '#1E5AA8'
        raw = (self.overlay_color or '').strip()
        alpha = max(0, min(self.overlay_opacity or 0, 100)) / 100

        if raw.startswith('rgba(') or raw.startswith('rgb('):
            payload = raw[raw.find('(') + 1: raw.rfind(')')]
            channels = [chunk.strip() for chunk in payload.split(',')]
            if len(channels) >= 3:
                try:
                    r = int(float(channels[0]))
                    g = int(float(channels[1]))
                    b = int(float(channels[2]))
                    color = f'rgba({r},{g},{b},{alpha:.2f})'
                except ValueError:
                    color = raw
            else:
                color = raw
        elif raw.startswith('#'):
            hex_value = raw.lstrip('#')
            if len(hex_value) == 3:
                hex_value = ''.join(ch * 2 for ch in hex_value)
            if len(hex_value) == 6:
                try:
                    r = int(hex_value[0:2], 16)
                    g = int(hex_value[2:4], 16)
                    b = int(hex_value[4:6], 16)
                    color = f'rgba({r},{g},{b},{alpha:.2f})'
                except ValueError:
                    color = raw
            else:
                color = raw
        elif raw:
            color = raw
        else:
            color = f'rgba(11,31,58,{alpha:.2f})'

        return ';'.join([
            f'--fa-gateway-accent:{accent}',
            f'--fa-gateway-overlay:{color}',
        ])

# ── /fa-new/ Navigation Menu ──────────────────────────────────────────────────
# Dynamic nav menu items for the Persian front page.
# Supports one level of submenu via the `parent` FK.

class FaNavMenuItem(models.Model):
    """One item in the Persian front-page navigation bar.

    Top-level items (parent=None) appear directly in the nav.
    Child items (parent set) appear as a dropdown submenu under their parent.
    """

    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children',
        verbose_name='زیرمنوی',
        help_text='اگر این آیتم زیرمنوی یک آیتم دیگر است، آن را اینجا انتخاب کنید.',
    )
    label = models.CharField(
        max_length=100,
        verbose_name='متن لینک',
        help_text='متنی که در منو نمایش داده می‌شود.',
    )
    url = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='لینک',
        help_text='برای منوی اصلی با زیرمنو خالی بگذارید. برای زیرمنو آدرس صفحه را وارد کنید.',
    )
    order = models.PositiveIntegerField(
        default=0, db_index=True,
        verbose_name='ترتیب نمایش',
        help_text='عدد کوچک‌تر = چپ‌تر در نوار ناوبری',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
        help_text='غیرفعال کردن این آیتم را از منو پنهان می‌کند.',
    )
    open_in_new_tab = models.BooleanField(
        default=False,
        verbose_name='باز کردن در تب جدید',
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'آیتم منوی فارسی'
        verbose_name_plural = 'منوی ناوبری صفحه فارسی'

    def __str__(self):
        prefix = f'↳ {self.parent.label} / ' if self.parent_id else ''
        return f'{prefix}{self.label}'


# ── /fa-new/ Footer Settings ──────────────────────────────────────────────────
# Singleton — controls the footer block on the Persian front page.

class FaFooterSettings(models.Model):
    """Singleton settings for the footer of the /fa-new/ Persian page."""

    # ── Brand column ──────────────────────────────────────────────────────────
    brand_name = models.CharField(
        max_length=150, blank=True, default='آدونیس | ADONIS',
        verbose_name='نام برند',
    )
    brand_tagline = models.CharField(
        max_length=250, blank=True, default='گروه توسعه و مشاوره اقامت در آتن',
        verbose_name='شعار / توضیح کوتاه برند',
    )
    footer_logo = models.ImageField(
        upload_to='fa-new/footer/', blank=True, null=True,
        verbose_name='لوگوی فوتر',
        help_text='PNG با پس‌زمینه شفاف — اختیاری. اگر خالی باشد از لوگوی هدر استفاده می‌شود.',
    )
    logo_max_width = models.PositiveIntegerField(
        default=120,
        verbose_name='عرض لوگو (px)',
        help_text='حداکثر عرض لوگو در فوتر به پیکسل. پیش‌فرض: ۱۲۰',
    )

    # ── Contact column ────────────────────────────────────────────────────────
    contact_title = models.CharField(
        max_length=100, blank=True, default='تماس',
        verbose_name='عنوان ستون تماس',
    )
    address = models.CharField(
        max_length=300, blank=True,
        default='آتن، آلیموس، خیابان پوزیدوناس، شماره ۷۸',
        verbose_name='آدرس',
    )
    phone = models.CharField(
        max_length=50, blank=True, default='+30 698 598 9596',
        verbose_name='شماره تلفن',
    )
    email = models.EmailField(
        blank=True, default='info@adonisgroup.gr',
        verbose_name='ایمیل',
    )
    whatsapp_url = models.CharField(
        max_length=300, blank=True, default='https://wa.me/306985989596',
        verbose_name='لینک واتس‌اپ',
        help_text='مثال: https://wa.me/306985989596',
    )

    # ── Links column ──────────────────────────────────────────────────────────
    links_title = models.CharField(
        max_length=100, blank=True, default='دسترسی سریع',
        verbose_name='عنوان ستون لینک‌ها',
    )

    # ── Bottom bar ────────────────────────────────────────────────────────────
    copyright_text = models.CharField(
        max_length=300, blank=True,
        default='© آدونیس گروپ — همه حقوق محفوظ است.',
        verbose_name='متن کپی‌رایت',
    )
    footer_tag = models.CharField(
        max_length=150, blank=True,
        default='نسخه پیش‌نمایش فارسی · /fa-new/',
        verbose_name='برچسب پایین فوتر',
        help_text='متن کوچک سمت راست نوار پایین فوتر.',
    )

    # ── Social links ──────────────────────────────────────────────────────────
    instagram_url = models.CharField(
        max_length=300, blank=True, verbose_name='لینک اینستاگرام',
    )
    linkedin_url = models.CharField(
        max_length=300, blank=True, verbose_name='لینک لینکدین',
    )
    telegram_url = models.CharField(
        max_length=300, blank=True, verbose_name='لینک تلگرام',
    )
    youtube_url = models.CharField(
        max_length=300, blank=True, verbose_name='لینک یوتیوب',
        help_text='مثال: https://youtube.com/@adonisgroup',
    )
    facebook_url = models.CharField(
        max_length=300, blank=True, verbose_name='لینک فیسبوک',
    )
    x_url = models.CharField(
        max_length=300, blank=True, verbose_name='لینک ایکس (توییتر)',
        help_text='مثال: https://x.com/adonisgroup',
    )

    # ── Offices (Tehran + Athens) ───────────────────────────────────────────────
    tehran_address = models.CharField(
        max_length=300, blank=True,
        verbose_name='نشانی دفتر تهران',
        help_text='نشانی کامل دفتر تهران.',
    )
    tehran_phone = models.CharField(
        max_length=120, blank=True,
        verbose_name='تلفن دفتر تهران',
        help_text='می‌توانید چند شماره را با «/» از هم جدا کنید.',
    )
    athens_address = models.CharField(
        max_length=300, blank=True,
        default='آتن، آلیموس، خیابان پوزیدوناس، شماره ۷۸',
        verbose_name='نشانی دفتر آتن',
    )
    athens_phone = models.CharField(
        max_length=120, blank=True, default='+30 698 598 9596',
        verbose_name='تلفن دفتر آتن',
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        verbose_name = 'تنظیمات فوتر صفحه فارسی'
        verbose_name_plural = 'تنظیمات فوتر صفحه فارسی'

    def __str__(self):
        return 'تنظیمات فوتر صفحه فارسی'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
