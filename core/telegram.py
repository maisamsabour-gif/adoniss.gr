"""
Telegram Bot notification utility for Adonis Group.
Sends contact form submissions and property interest requests to Telegram.
"""
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)


def _fmt_phone(raw):
    """Ensure phone includes leading '+' for international display."""
    if not raw or raw.strip() == '':
        return '—'
    p = raw.strip()
    if not p.startswith('+'):
        p = '+' + p
    return p


def send_telegram_message(bot_token, chat_id, message, parse_mode='HTML'):
    """
    Send a message via Telegram Bot API.
    
    Args:
        bot_token: Telegram bot token from @BotFather
        chat_id: Target chat/group ID
        message: Text message (supports HTML formatting)
        parse_mode: 'HTML' or 'Markdown'
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not bot_token or not chat_id:
        logger.warning('Telegram: bot_token or chat_id not configured')
        return False

    # Prepend a per-server source label (e.g. "🇮🇷 سایت فارسی") so that when
    # several sites share one bot/group, each lead is clearly attributable.
    # Configured via the TELEGRAM_SOURCE_LABEL env var; empty = no prefix.
    try:
        from django.conf import settings as _dj_settings
        _label = (getattr(_dj_settings, 'TELEGRAM_SOURCE_LABEL', '') or '').strip()
    except Exception:
        _label = ''
    if _label:
        if parse_mode == 'HTML':
            message = f'<b>{_label}</b>\n{message}'
        else:
            message = f'{_label}\n{message}'

    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    data = urllib.parse.urlencode({
        'chat_id': chat_id,
        'text': message,
        'parse_mode': parse_mode,
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                logger.info(f'Telegram: message sent to {chat_id}')
                return True
            else:
                logger.error(f'Telegram API error: {result}')
                return False
    except Exception as e:
        logger.error(f'Telegram send failed: {e}')
        return False


def notify_new_contact(contact_submission):
    """
    Send notification about a new contact form submission.

    Args:
        contact_submission: ContactSubmission model instance
    """
    from .models import SiteSettings
    from django.conf import settings as django_settings
    import html as _html

    # Source → human label + flag emoji
    _SOURCE_LABELS = {
        'fa_landing_modal':      ('🇮🇷 Landing FA',      'فارسی'),
        'fa_new_consult_modal':  ('🇮🇷 سایت فارسی',       'فارسی'),
        'consultation_modal':    ('🌐 Global Modal',      'EN/TR'),
        'contact_page':          ('📋 Contact Page',      'EN/TR'),
        'modal_form':            ('🖥 Modal Form',        'EN/TR'),
        'public_contact_page':   ('📋 Contact Page',      'EN/TR'),
    }

    try:
        site = SiteSettings.objects.first()
        if not site or not site.telegram_enabled:
            return False

        from .models import REQUEST_TYPES
        request_type_display = dict(REQUEST_TYPES).get(
            contact_submission.request_type, contact_submission.request_type
        )

        source_key = getattr(contact_submission, 'source', '') or ''
        source_label, lang_label = _SOURCE_LABELS.get(source_key, ('🌐 Website', '—'))

        # Admin deep-link
        try:
            base = getattr(django_settings, 'SITE_URL', 'https://adonisgroup.gr').rstrip('/')
            admin_url = f'{base}/admin/core/contactsubmission/{contact_submission.pk}/change/'
        except Exception:
            admin_url = ''

        name  = _html.escape(contact_submission.full_name or '—')
        phone = _html.escape(_fmt_phone(contact_submission.phone))
        email = _html.escape(contact_submission.email or '—')
        ts    = contact_submission.created_at.strftime('%Y-%m-%d %H:%M')

        message = (
            f"📩 <b>New Contact Request</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Name:</b> {name}\n"
            f"📞 <b>Phone:</b> <code>{phone}</code>\n"
            f"📧 <b>Email:</b> {email}\n"
            f"📋 <b>Type:</b> {request_type_display}\n"
            f"🔖 <b>Source:</b> {source_label}  |  <b>Lang:</b> {lang_label}\n"
        )

        if contact_submission.message:
            msg_text = _html.escape(contact_submission.message[:300])
            message += f"\n💬 <b>Message:</b>\n{msg_text}\n"

        if contact_submission.property_interest:
            message += f"🏠 <b>Property:</b> {_html.escape(contact_submission.property_interest)}\n"

        message += f"\n🕐 <b>Time:</b> {ts}\n"

        if admin_url:
            message += f"🔗 <a href=\"{admin_url}\">View in Admin</a>\n"

        message += "━━━━━━━━━━━━━━━━━━━━\n🌐 <i>Adonis Group Website</i>"

        return send_telegram_message(
            site.telegram_bot_token,
            site.telegram_chat_id,
            message
        )
    except Exception as e:
        logger.error(f'notify_new_contact failed: {e}')
        return False


def notify_chat_lead(chat_lead, conversation=None):
    """
    Send a clean, formatted Telegram notification when a chat-widget lead is captured.

    Message format:
        🚨 New Chat Lead

        📞 Phone: +30xxxxxxxxx
        🌍 Page: /greece-golden-visa/
        🗣 Language: English
        🕒 Time: 2026-03-07 15:40

        📝 Summary:
        Visitor asked about Greece Golden Visa and requested a callback.

        💬 Last message:
        "I want more information about Athens properties"

        🔗 Admin:
        https://adonisgroup.gr/admin/...

    Never raises — errors are logged and the lead is preserved regardless.
    """
    from .models import SiteSettings
    from django.conf import settings as django_settings
    import html as _html

    # Map 2-letter language codes to full readable names
    _LANG_NAMES = {
        'EN': 'English', 'FA': 'Persian (Farsi)', 'EL': 'Greek',
        'TR': 'Turkish',  'AR': 'Arabic',          'RU': 'Russian',
        'DE': 'German',   'FR': 'French',           'ZH': 'Chinese',
    }

    try:
        site = SiteSettings.objects.first()
        if not site or not site.telegram_enabled:
            logger.info('notify_chat_lead: Telegram disabled or no SiteSettings')
            return False

        convo = conversation if conversation is not None else (chat_lead.conversation_json or [])

        # ── Admin URL ────────────────────────────────────────────────────────
        try:
            base      = getattr(django_settings, 'SITE_URL', 'https://adonisgroup.gr').rstrip('/')
            admin_url = f'{base}/admin/core/chatlead/{chat_lead.pk}/change/'
        except Exception:
            admin_url = ''

        # ── Page path (strip domain, keep path only for brevity) ─────────────
        page = chat_lead.page_url or ''
        try:
            from urllib.parse import urlparse
            parsed = urlparse(page)
            page = parsed.path or page   # "/greece-golden-visa/" is cleaner in Telegram
        except Exception:
            pass

        # ── Language ─────────────────────────────────────────────────────────
        lang_code = (chat_lead.language or '').upper()
        lang_label = _LANG_NAMES.get(lang_code, lang_code or 'Unknown')

        # ── Timestamp ────────────────────────────────────────────────────────
        ts = chat_lead.created_at.strftime('%Y-%m-%d %H:%M')

        # ── Summary ──────────────────────────────────────────────────────────
        summary = _html.escape((chat_lead.summary or '').strip())

        # ── Last user message ────────────────────────────────────────────────
        last_user_msg = ''
        for m in reversed(convo):
            if m.get('role') == 'user':
                raw = (m.get('text', '') or m.get('content', '')).strip()
                if raw:
                    last_user_msg = _html.escape(raw[:200])
                    break

        # ── Build message ────────────────────────────────────────────────────
        msg = '🚨 <b>New Chat Lead</b>\n\n'

        msg += f'📞 <b>Phone:</b> <code>{_html.escape(chat_lead.phone)}</code>\n'
        if page:
            msg += f'🌍 <b>Page:</b> {_html.escape(page)}\n'
        if lang_label:
            msg += f'🗣 <b>Language:</b> {lang_label}\n'
        msg += f'🕒 <b>Time:</b> {ts}\n'

        if summary:
            msg += f'\n📝 <b>Summary:</b>\n{summary}\n'

        if last_user_msg:
            msg += f'\n💬 <b>Last message:</b>\n&#8220;{last_user_msg}&#8221;\n'

        if admin_url:
            msg += f'\n🔗 <b>Admin:</b>\n{admin_url}'

        ok = send_telegram_message(site.telegram_bot_token, site.telegram_chat_id, msg)
        if ok:
            logger.info('notify_chat_lead: sent for lead pk=%s', chat_lead.pk)
        else:
            logger.warning('notify_chat_lead: send failed for lead pk=%s', chat_lead.pk)
        return ok

    except Exception as exc:
        logger.error('notify_chat_lead exception for lead pk=%s: %s', getattr(chat_lead, 'pk', '?'), exc)
        return False


def notify_agent_needed(session, trigger='interest'):
    """
    Notify agents via Telegram that a visitor is showing serious interest
    and is waiting for a human agent to join the chat.
    """
    from .models import SiteSettings
    from django.conf import settings as django_settings

    try:
        site = SiteSettings.objects.first()
        if not site or not site.telegram_enabled:
            return False

        # Build conversation preview (last 10 messages)
        msgs = session.session_messages.order_by('created_at')[:15]
        convo = ''
        for m in msgs:
            icon = '👤' if m.role == 'user' else '🤖'
            convo += f'{icon} {m.content[:120]}\n'

        # Build admin live-chat link
        try:
            base = getattr(django_settings, 'SITE_URL', 'https://adonisgroup.gr')
            chat_url = f'{base}/staff/chat/{session.session_key}/'
        except Exception:
            chat_url = ''

        message = (
            f'🔔 <b>Live Chat — Agent Needed</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━\n\n'
            f'🎯 <b>Trigger:</b> {trigger}\n'
            f'🌐 <b>Page:</b> {session.page_url or "—"}\n'
            f'⏱ <b>Started:</b> {session.created_at.strftime("%H:%M")}\n\n'
        )
        if convo:
            message += f'💬 <b>Conversation so far:</b>\n{convo}\n'
        if chat_url:
            message += f'👉 <a href="{chat_url}">Open Live Chat</a>\n'
        message += '━━━━━━━━━━━━━━━━━━━━\n🌐 <i>Adonis Group – Live Chat</i>'

        return send_telegram_message(site.telegram_bot_token, site.telegram_chat_id, message)
    except Exception as e:
        logger.error(f'notify_agent_needed failed: {e}')
        return False


def notify_property_interest(interest):
    """
    Send notification about a new property interest request.
    
    Args:
        interest: PropertyInterest model instance
    """
    from .models import SiteSettings
    
    try:
        settings = SiteSettings.objects.first()
        if not settings or not settings.telegram_enabled:
            return False
        
        property_title = interest.property.name if interest.property else 'N/A'
        
        message = (
            f"🏠 <b>Property Interest</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Name:</b> {interest.full_name}\n"
            f"📞 <b>Phone:</b> <code>{_fmt_phone(interest.phone)}</code>\n"
            f"📧 <b>Email:</b> {interest.email}\n"
            f"🏡 <b>Property:</b> {property_title}\n"
        )
        
        if hasattr(interest, 'message') and interest.message:
            message += f"💬 <b>Message:</b>\n{interest.message}\n"
        
        message += (
            f"\n🕐 <b>Time:</b> {interest.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 <i>Adonis Group Website</i>"
        )
        
        return send_telegram_message(
            settings.telegram_bot_token,
            settings.telegram_chat_id,
            message
        )
    except Exception as e:
        logger.error(f'notify_property_interest failed: {e}')
        return False


def notify_unit_booking(booking):
    """
    Send notification about a new unit booking request.
    """
    from .models import SiteSettings
    
    try:
        settings = SiteSettings.objects.first()
        if not settings or not settings.telegram_enabled:
            return False
        
        unit = booking.unit
        property_name = unit.property.name if unit.property else 'N/A'
        
        message = (
            f"🔑 <b>Unit Booking Request</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Name:</b> {booking.full_name}\n"
            f"📞 <b>Phone:</b> <code>{_fmt_phone(booking.phone)}</code>\n"
            f"📧 <b>Email:</b> {booking.email}\n"
            f"🏡 <b>Property:</b> {property_name}\n"
            f"🏢 <b>Unit:</b> {unit.unit_label}\n"
            f"💰 <b>Price:</b> €{unit.price:,.0f}\n"
        )
        
        if booking.message:
            message += f"💬 <b>Message:</b>\n{booking.message}\n"
        
        message += (
            f"\n🕐 <b>Time:</b> {booking.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 <i>Adonis Group Website</i>"
        )
        
        return send_telegram_message(
            settings.telegram_bot_token,
            settings.telegram_chat_id,
            message
        )
    except Exception as e:
        logger.error(f'notify_unit_booking failed: {e}')
        return False


def notify_partner_lead(lead):
    """
    Send notification about a new partnership enquiry.

    Args:
        lead: PartnerLead model instance
    """
    from .models import SiteSettings

    try:
        settings = SiteSettings.objects.first()
        if not settings or not settings.telegram_enabled:
            return False

        type_display = (
            lead.get_partner_type_display()
            if lead.partner_type != 'other'
            else f"Other – {lead.other_title or ''}"
        )

        message = (
            f"🤝 <b>New Partnership Lead</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Name:</b> {lead.full_name}\n"
            f"📞 <b>Phone:</b> <code>{_fmt_phone(lead.phone)}</code>\n"
            f"📧 <b>Email:</b> {lead.email}\n"
            f"🏷 <b>Type:</b> {type_display}\n"
        )

        if lead.country:
            message += f"🌍 <b>Country:</b> {lead.country}\n"
        if lead.company:
            message += f"🏢 <b>Company:</b> {lead.company}\n"
        if lead.message:
            message += f"💬 <b>Message:</b>\n{lead.message}\n"

        message += (
            f"\n🕐 <b>Time:</b> {lead.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 <i>Adonis Group – Partnerships Page</i>"
        )

        return send_telegram_message(
            settings.telegram_bot_token,
            settings.telegram_chat_id,
            message
        )
    except Exception as e:
        logger.error(f'notify_partner_lead failed: {e}')
        return False
